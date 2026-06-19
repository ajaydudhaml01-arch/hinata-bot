/**
 * CSInterface.js — Adobe CEP CSInterface Library (v11.x compatible)
 * Minimal implementation providing the core evalScript functionality
 * required by AE PowerTools. For the full official library, replace
 * this file with the one from:
 * https://github.com/nicokant/Adobe-CEP/blob/master/CEP_11.x/CSInterface.js
 *
 * This build covers: evalScript, getSystemPath, addEventListener,
 * requestOpenExtension, and closeExtension.
 */

var SystemPath = {
    USER_DATA: "userData",
    COMMON_FILES: "commonFiles",
    MY_DOCUMENTS: "myDocuments",
    APPLICATION: "application",
    EXTENSION: "extension",
    HOST_APPLICATION: "hostApplication"
};

var ColorType = {
    RGB: "rgb",
    GRADIENT: "gradient",
    NONE: "none"
};

function CSEvent(type, scope, appId, extensionId) {
    this.type = type;
    this.scope = scope || "APPLICATION";
    this.appId = appId || "";
    this.extensionId = extensionId || "";
    this.data = "";
}

function CSInterface() {}

CSInterface.prototype.CYCRIPT_CALL_TIMEOUT_DEFAULT = 5000;
CSInterface.CYCRIPT_CALL_TIMEOUT_DEFAULT = 5000;

CSInterface.prototype.getHostEnvironment = function () {
    try {
        return JSON.parse(window.__adobe_cep__.getHostEnvironment());
    } catch (e) {
        return {};
    }
};

CSInterface.prototype.closeExtension = function () {
    try {
        window.__adobe_cep__.closeExtension();
    } catch (e) {}
};

CSInterface.prototype.getSystemPath = function (pathType) {
    try {
        return window.__adobe_cep__.getSystemPath(pathType);
    } catch (e) {
        return "";
    }
};

CSInterface.prototype.evalScript = function (script, callback) {
    try {
        if (callback === null || callback === undefined) {
            callback = function () {};
        }
        window.__adobe_cep__.evalScript(script, callback);
    } catch (e) {
        if (callback) callback('{"success":false,"message":"CSInterface evalScript error: ' + e.message + '"}');
    }
};

CSInterface.prototype.getApplicationID = function () {
    var hostEnv = this.getHostEnvironment();
    return hostEnv && hostEnv.appId ? hostEnv.appId : "";
};

CSInterface.prototype.getHostCapabilities = function () {
    try {
        return JSON.parse(window.__adobe_cep__.getHostCapabilities());
    } catch (e) {
        return {};
    }
};

CSInterface.prototype.dispatchEvent = function (event) {
    if (typeof event.data === "undefined") event.data = "";
    try {
        window.__adobe_cep__.dispatchEvent(event);
    } catch (e) {}
};

CSInterface.prototype.addEventListener = function (type, listener, obj) {
    try {
        window.__adobe_cep__.addEventListener(type, listener, obj);
    } catch (e) {}
};

CSInterface.prototype.removeEventListener = function (type, listener, obj) {
    try {
        window.__adobe_cep__.removeEventListener(type, listener, obj);
    } catch (e) {}
};

CSInterface.prototype.requestOpenExtension = function (extensionId, params) {
    try {
        window.__adobe_cep__.requestOpenExtension(extensionId, params || "");
    } catch (e) {}
};

CSInterface.prototype.getExtensions = function (extensionIds) {
    try {
        var exts = JSON.parse(window.__adobe_cep__.getExtensions(extensionIds));
        return exts;
    } catch (e) {
        return [];
    }
};

CSInterface.prototype.getNetworkPreferences = function () {
    try {
        return JSON.parse(window.__adobe_cep__.getNetworkPreferences());
    } catch (e) {
        return {};
    }
};

CSInterface.prototype.getCurrentApiVersion = function () {
    try {
        return JSON.parse(window.__adobe_cep__.getCurrentApiVersion());
    } catch (e) {
        return { major: 11, minor: 0, micro: 0 };
    }
};

CSInterface.prototype.setPanelFlyoutMenu = function (menu) {
    try {
        window.__adobe_cep__.invokeSync("setPanelFlyoutMenu", menu);
    } catch (e) {}
};

CSInterface.prototype.openURLInDefaultBrowser = function (url) {
    try {
        if (typeof cep !== "undefined" && cep.util) {
            cep.util.openURLInDefaultBrowser(url);
        } else {
            window.__adobe_cep__.openURLInDefaultBrowser(url);
        }
    } catch (e) {}
};

CSInterface.prototype.getExtensionID = function () {
    try {
        return window.__adobe_cep__.getExtensionId();
    } catch (e) {
        return "";
    }
};

CSInterface.prototype.getScaleFactor = function () {
    try {
        return parseFloat(window.__adobe_cep__.getScaleFactor());
    } catch (e) {
        return 1;
    }
};

CSInterface.prototype.setScaleFactorChangedHandler = function (handler) {
    try {
        window.__adobe_cep__.setScaleFactorChangedHandler(handler);
    } catch (e) {}
};

CSInterface.prototype.getCurrentImsUserId = function () {
    try {
        return window.__adobe_cep__.getCurrentImsUserId();
    } catch (e) {
        return "";
    }
};

CSInterface.prototype.imsConnect = function (options) {
    try {
        return JSON.parse(window.__adobe_cep__.imsConnect(JSON.stringify(options)));
    } catch (e) {
        return {};
    }
};

CSInterface.prototype.imsDisconnect = function (imsRef) {
    try {
        window.__adobe_cep__.imsDisconnect(imsRef);
    } catch (e) {}
};

CSInterface.prototype.imsFetchAccounts = function (imsRef, clientId) {
    try {
        return JSON.parse(window.__adobe_cep__.imsFetchAccounts(imsRef, clientId));
    } catch (e) {
        return [];
    }
};

CSInterface.prototype.imsFetchAccessToken = function (imsRef, clientId, clientSecret, userAccountGuid, serviceAccountGuid, scope) {
    try {
        return JSON.parse(window.__adobe_cep__.imsFetchAccessToken(imsRef, clientId, clientSecret, userAccountGuid, serviceAccountGuid, scope));
    } catch (e) {
        return {};
    }
};

CSInterface.prototype.imsSetProxyCredentials = function (proxyUsername, proxyPassword) {
    try {
        window.__adobe_cep__.imsSetProxyCredentials(proxyUsername, proxyPassword);
    } catch (e) {}
};

CSInterface.prototype.getMonitorScaleFactor = function () {
    try {
        return parseFloat(window.__adobe_cep__.getMonitorScaleFactor());
    } catch (e) {
        return 1;
    }
};

CSInterface.prototype.registerInvalidCertificateCallback = function (callback) {
    try {
        window.__adobe_cep__.registerInvalidCertificateCallback(callback);
    } catch (e) {}
};

CSInterface.prototype.registerKeyEventsInterest = function (keyEventsInterest) {
    try {
        return window.__adobe_cep__.registerKeyEventsInterest(keyEventsInterest);
    } catch (e) {}
};

CSInterface.prototype.setWindowTitle = function (title) {
    try {
        window.__adobe_cep__.invokeSync("setWindowTitle", title);
    } catch (e) {}
};

CSInterface.prototype.getWindowTitle = function () {
    try {
        return window.__adobe_cep__.invokeSync("getWindowTitle", "");
    } catch (e) {
        return "";
    }
};
