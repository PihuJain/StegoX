package com.pydroidx.stegox;

import androidx.lifecycle.ViewModel;

public class MainViewModel extends ViewModel {
    private final WebModel webModel;

    public MainViewModel() {
        this.webModel = new WebModel();
    }

    public String getUrl() {
        return webModel.getStegoXUrl();
    }

    public String getAppTitle() {
        return webModel.getAppTitle();
    }

    public boolean isUrlValid() {
        return webModel.isValidUrl();
    }
} 