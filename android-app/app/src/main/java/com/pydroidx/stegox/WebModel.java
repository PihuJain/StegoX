package com.pydroidx.stegox;

public class WebModel {
    // TODO: Replace with your actual server URL when deploying
    // For local development, you can use: http://localhost:8501
    // For production, use your deployed server URL
    private static final String STEGO_X_URL = "http://localhost:8501";
    private static final String APP_TITLE = "StegoX";
    private static final String FALLBACK_URL = "http://localhost:8501";

    public String getStegoXUrl() {
        return STEGO_X_URL;
    }

    public String getFallbackUrl() {
        return FALLBACK_URL;
    }

    public String getAppTitle() {
        return APP_TITLE;
    }

    public boolean isValidUrl() {
        return STEGO_X_URL != null && 
               (STEGO_X_URL.startsWith("http://") || STEGO_X_URL.startsWith("https://"));
    }

    public boolean shouldEnableJavaScript() {
        return true;
    }

    public boolean shouldEnableDomStorage() {
        return true;
    }
} 