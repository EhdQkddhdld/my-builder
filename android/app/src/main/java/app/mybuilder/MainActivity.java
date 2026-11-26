package app.mybuilder;

import android.Manifest;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.media.MediaScannerConnection;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.HapticFeedbackConstants;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.Toast;
import android.window.OnBackInvokedDispatcher;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

/**
 * My Builder — 얇은 WebView 껍데기.
 * 내용(HTML)은 GitHub Pages(BuildConfig.APP_URL)에서 불러온다.
 *  - 앱을 열 때마다 HTML을 네트워크에서 새로 받아(캐시 우회) 보여 주고, 받은 사본을 앱 안에 저장한다.
 *  - 인터넷이 없으면 마지막으로 받은 사본으로 연다.
 *  - localStorage / IndexedDB(작가 목록, 기록·갤러리, API 키)는 앱 저장공간에 남아 앱을 업데이트해도 유지된다.
 */
public class MainActivity extends Activity {
    private static final String APP_URL = BuildConfig.APP_URL;
    private static final int REQ_FILE = 1001;
    private static final int REQ_PERM = 1002;
    private static final String FOLDER = "MyBuilder";

    private WebView web;
    private ValueCallback<Uri[]> fileCb;
    private File offlineHtml;
    private long lastHapticAt;
    private String lastHapticKind = "";

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        offlineHtml = new File(getFilesDir(), "offline/index.html");

        getWindow().setStatusBarColor(Color.parseColor("#0B0B0F"));
        getWindow().setNavigationBarColor(Color.parseColor("#0B0B0F"));

        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.parseColor("#0B0B0F"));
        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#0B0B0F"));
        root.addView(web, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(root);

        // 안드로이드 15+ 는 화면 끝까지 그리기가 강제됨 → 상태바/내비바/키보드만큼 안쪽 여백
        if (Build.VERSION.SDK_INT >= 30) {
            root.setOnApplyWindowInsetsListener((v, insets) -> {
                android.graphics.Insets i = insets.getInsets(WindowInsets.Type.systemBars()
                        | WindowInsets.Type.displayCutout() | WindowInsets.Type.ime());
                v.setPadding(i.left, i.top, i.right, i.bottom);
                return WindowInsets.CONSUMED;
            });
        }

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        s.setTextZoom(100);               // 휴대폰 글꼴 크기 설정이 레이아웃을 깨지 않게
        s.setSupportZoom(false);
        s.setMediaPlaybackRequiresUserGesture(true);
        s.setUserAgentString(s.getUserAgentString() + " MyBuilderApp/" + BuildConfig.VERSION_NAME);
        CookieManager.getInstance().setAcceptCookie(true);

        web.addJavascriptInterface(new Bridge(), "AndroidBridge");
        web.setWebViewClient(new Client());
        web.setWebChromeClient(new Chrome());
        web.setDownloadListener((url, ua, cd, mime, len) -> openExternal(Uri.parse(url)));

        if (Build.VERSION.SDK_INT >= 33) {
            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
                    OnBackInvokedDispatcher.PRIORITY_DEFAULT, this::handleBack);
        }

        if (state != null) web.restoreState(state);
        if (web.getUrl() == null) web.loadUrl(APP_URL);
    }

    // ---------- 뒤로가기: 웹의 window.rdHandleBack() 이 true면 창 하나만 닫힘, false면 앱 종료 ----------
    private void handleBack() {
        web.evaluateJavascript(
                "(function(){try{return !!(window.rdHandleBack&&window.rdHandleBack());}catch(e){return false;}})()",
                v -> { if (!"true".equals(v)) finish(); });
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        handleBack();
    }

    @Override protected void onSaveInstanceState(Bundle out) { super.onSaveInstanceState(out); web.saveState(out); }
    @Override protected void onPause() { super.onPause(); web.onPause(); CookieManager.getInstance().flush(); }
    @Override protected void onResume() { super.onResume(); web.onResume(); }
    @Override protected void onDestroy() { if (web != null) { web.destroy(); } super.onDestroy(); }

    // ---------- 페이지 로딩 ----------
    private boolean isAppDoc(Uri u) {
        Uri base = Uri.parse(APP_URL);
        if (u == null || !base.getScheme().equals(u.getScheme()) || !base.getHost().equalsIgnoreCase(u.getHost())
                || base.getPort() != u.getPort()) return false;
        String p = u.getPath() == null ? "" : u.getPath();
        String bp = base.getPath();
        return p.equals(bp) || p.equals(bp + "index.html") || p.equals(bp.substring(0, bp.length() - 1));
    }

    private boolean isOwnHost(Uri u) {
        Uri b = Uri.parse(APP_URL);
        return u != null && b.getHost().equalsIgnoreCase(u.getHost()) && b.getPort() == u.getPort();
    }

    private class Client extends WebViewClient {
        @Override
        public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest req) {
            if (!req.isForMainFrame() || !"GET".equals(req.getMethod()) || !isAppDoc(req.getUrl())) return null;
            byte[] body = fetchFresh();
            if (body != null) saveOffline(body);
            else body = readOffline();
            if (body == null) body = offlinePage().getBytes(StandardCharsets.UTF_8);
            Map<String, String> h = new HashMap<>();
            h.put("Cache-Control", "no-store");
            return new WebResourceResponse("text/html", "utf-8", 200, "OK", h, new ByteArrayInputStream(body));
        }

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
            Uri u = req.getUrl();
            if (isOwnHost(u)) return false;
            openExternal(u);
            return true;
        }
    }

    /** 캐시를 건너뛰고 최신 HTML 받기. 실패하면 null. */
    private byte[] fetchFresh() {
        HttpURLConnection c = null;
        try {
            URL url = new URL(APP_URL + "index.html?rdv=" + System.currentTimeMillis());
            c = (HttpURLConnection) url.openConnection();
            c.setConnectTimeout(6000);
            c.setReadTimeout(20000);
            c.setUseCaches(false);
            c.setRequestProperty("Cache-Control", "no-cache");
            c.setRequestProperty("Pragma", "no-cache");
            if (c.getResponseCode() != 200) return null;
            try (InputStream in = c.getInputStream()) {
                ByteArrayOutputStream bo = new ByteArrayOutputStream(1 << 20);
                byte[] buf = new byte[65536];
                int n;
                while ((n = in.read(buf)) > 0) bo.write(buf, 0, n);
                byte[] b = bo.toByteArray();
                String head = new String(b, 0, Math.min(b.length, 4096), StandardCharsets.UTF_8).toLowerCase();
                if (b.length < 2000 || !head.contains("<html")) return null;
                return b;
            }
        } catch (Exception e) {
            return null;
        } finally {
            if (c != null) c.disconnect();
        }
    }

    private void saveOffline(byte[] b) {
        try {
            File dir = offlineHtml.getParentFile();
            if (dir != null && !dir.exists()) dir.mkdirs();
            File tmp = new File(dir, "index.html.tmp");
            try (FileOutputStream o = new FileOutputStream(tmp)) { o.write(b); }
            if (!tmp.renameTo(offlineHtml)) { offlineHtml.delete(); tmp.renameTo(offlineHtml); }
        } catch (Exception ignored) { }
    }

    private byte[] readOffline() {
        if (!offlineHtml.exists()) return null;
        try (InputStream in = new java.io.FileInputStream(offlineHtml)) {
            ByteArrayOutputStream bo = new ByteArrayOutputStream();
            byte[] buf = new byte[65536];
            int n;
            while ((n = in.read(buf)) > 0) bo.write(buf, 0, n);
            return bo.toByteArray();
        } catch (Exception e) {
            return null;
        }
    }

    private static String offlinePage() {
        return "<!DOCTYPE html><html lang=ko><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
                + "<title>My Builder</title><style>body{background:#0b0b0f;color:#e8e8ef;font:16px/1.6 sans-serif;display:flex;min-height:90vh;align-items:center;justify-content:center;text-align:center;padding:24px}"
                + "button{margin-top:16px;font-size:16px;padding:12px 22px;border-radius:12px;border:0;background:#b794f6;color:#111}</style></head>"
                + "<body><div><p>처음 한 번은 인터넷 연결이 필요해요.<br>연결한 뒤 다시 시도해 주세요.</p>"
                + "<button onclick='location.reload()'>다시 시도</button></div></body></html>";
    }

    private void openExternal(Uri u) {
        try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (ActivityNotFoundException ignored) { }
    }

    // ---------- 파일 선택(백업 불러오기) ----------
    private class Chrome extends WebChromeClient {
        @Override
        public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb, FileChooserParams p) {
            if (fileCb != null) fileCb.onReceiveValue(null);
            fileCb = cb;
            try {
                startActivityForResult(p.createIntent(), REQ_FILE);
            } catch (ActivityNotFoundException e) {
                fileCb = null;
                return false;
            }
            return true;
        }
    }

    @Override
    @SuppressWarnings("deprecation")
    protected void onActivityResult(int req, int res, Intent data) {
        if (req == REQ_FILE && fileCb != null) {
            fileCb.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(res, data));
            fileCb = null;
            return;
        }
        super.onActivityResult(req, res, data);
    }

    // ---------- JS 브리지 ----------
    private void toast(String m) { runOnUiThread(() -> Toast.makeText(this, m, Toast.LENGTH_SHORT).show()); }

    private static String safeName(String n) {
        if (n == null || n.trim().isEmpty()) n = "download";
        n = n.replaceAll("[\\\\/:*?\"<>|\\x00-\\x1f]", "_").trim();
        if (n.length() > 120) n = n.substring(n.length() - 120);
        return n;
    }

    private class Bridge {
        /** base64 데이터를 사진첩(이미지) 또는 다운로드 폴더(그 외)에 저장. 성공하면 true. */
        @JavascriptInterface
        public boolean saveBase64(String b64, String filename, String mime) {
            try {
                byte[] data = Base64.decode(b64, Base64.DEFAULT);
                String name = safeName(filename);
                if (mime == null || mime.isEmpty()) mime = "application/octet-stream";
                boolean image = mime.startsWith("image/");
                if (Build.VERSION.SDK_INT >= 29) {
                    ContentResolver r = getContentResolver();
                    ContentValues cv = new ContentValues();
                    cv.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
                    cv.put(MediaStore.MediaColumns.MIME_TYPE, mime);
                    cv.put(MediaStore.MediaColumns.RELATIVE_PATH,
                            (image ? Environment.DIRECTORY_PICTURES : Environment.DIRECTORY_DOWNLOADS) + "/" + FOLDER);
                    cv.put(MediaStore.MediaColumns.IS_PENDING, 1);
                    Uri col = image ? MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
                            : MediaStore.Downloads.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY);
                    Uri item = r.insert(col, cv);
                    if (item == null) return false;
                    try (OutputStream o = r.openOutputStream(item)) {
                        if (o == null) { r.delete(item, null, null); return false; }
                        o.write(data);
                    }
                    cv.clear();
                    cv.put(MediaStore.MediaColumns.IS_PENDING, 0);
                    r.update(item, cv, null, null);
                    return true;
                } else {
                    if (checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                        runOnUiThread(() -> requestPermissions(new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, REQ_PERM));
                        toast("저장 권한을 허용한 뒤 다시 눌러 주세요");
                        return false;
                    }
                    File dir = new File(Environment.getExternalStoragePublicDirectory(
                            image ? Environment.DIRECTORY_PICTURES : Environment.DIRECTORY_DOWNLOADS), FOLDER);
                    if (!dir.exists()) dir.mkdirs();
                    File f = new File(dir, name);
                    try (FileOutputStream o = new FileOutputStream(f)) { o.write(data); }
                    MediaScannerConnection.scanFile(MainActivity.this, new String[]{f.getAbsolutePath()}, new String[]{mime}, null);
                    return true;
                }
            } catch (Exception e) {
                return false;
            }
        }

        @JavascriptInterface
        public void copyText(String t) {
            runOnUiThread(() -> {
                ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                if (cm != null) cm.setPrimaryClip(ClipData.newPlainText("prompt", t == null ? "" : t));
            });
        }

        // Legacy bridge entry point remains available to saved/older HTML.
        @JavascriptInterface
        public void haptic() {
            hapticKind("tap", "normal");
        }

        @JavascriptInterface
        public void hapticKind(String kind, String strength) {
            if (kind == null) return;
            final int effect;
            switch (kind) {
                case "tap":
                    effect = "weak".equals(strength) ? HapticFeedbackConstants.CLOCK_TICK
                            : "strong".equals(strength) ? HapticFeedbackConstants.CONTEXT_CLICK
                            : HapticFeedbackConstants.KEYBOARD_TAP;
                    break;
                case "step": effect = HapticFeedbackConstants.CLOCK_TICK; break;
                case "heavy": effect = HapticFeedbackConstants.LONG_PRESS; break;
                case "copy": effect = HapticFeedbackConstants.CONTEXT_CLICK; break;
                case "success": effect = Build.VERSION.SDK_INT >= 30
                        ? HapticFeedbackConstants.CONFIRM : HapticFeedbackConstants.CONTEXT_CLICK; break;
                case "warn": effect = Build.VERSION.SDK_INT >= 30
                        ? HapticFeedbackConstants.REJECT : HapticFeedbackConstants.LONG_PRESS; break;
                default: return;
            }
            runOnUiThread(() -> {
                if (web == null || isFinishing() || isDestroyed() || !web.isShown() || !hasWindowFocus()) return;
                long now = android.os.SystemClock.elapsedRealtime();
                if (kind.equals(lastHapticKind) && now - lastHapticAt < 80L) return;
                lastHapticKind = kind;
                lastHapticAt = now;
                // No IGNORE_* flags: respect system and view haptic settings.
                web.performHapticFeedback(effect);
            });
        }

        @JavascriptInterface
        public void shareText(String t) {
            runOnUiThread(() -> {
                Intent i = new Intent(Intent.ACTION_SEND);
                i.setType("text/plain");
                i.putExtra(Intent.EXTRA_TEXT, t == null ? "" : t);
                try { startActivity(Intent.createChooser(i, "공유")); } catch (Exception ignored) { }
            });
        }

        @JavascriptInterface
        public String appVersion() { return BuildConfig.VERSION_NAME; }
    }
}
