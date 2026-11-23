(function () {
    "use strict";
    const supported = ["ko", "en", "ja", "zh-CN"];
    const fallback = "ko";
    const storageKey = "dataToolkit.locale";
    const catalogs = window.DataToolkitLocales || {};
    const isSupported = code => supported.includes(code);
    const normalize = code => isSupported(code) ? code : fallback;
    const saved = (() => {
        try { return localStorage.getItem(storageKey); } catch { return null; }
    })();
    let current = normalize(saved);
    const getGroup = (code, name) => catalogs[code]?.[name] || {};
    const group = name => Object.fromEntries(supported.map(code => [code, new Proxy(getGroup(code, name), {
        get(target, key) { return target[key] ?? getGroup(fallback, name)[key]; }
    })]));
    const lookup = (key, name = "messages") => {
        const value = getGroup(current, name)[key] ?? getGroup(fallback, name)[key];
        if (value === undefined) {
            if (window.location.hostname === "localhost") console.warn(`Missing translation: ${name}.${key}`);
            return key;
        }
        return value;
    };
    const t = (key, params = {}, name = "messages") => lookup(key, name).replace(/\{([a-zA-Z][a-zA-Z0-9_]*)\}/g, (match, field) =>
        Object.prototype.hasOwnProperty.call(params, field) ? String(params[field]) : match);
    const translate = () => {
        document.documentElement.lang = current;
        const locale = document.getElementById("locale");
        if (locale) locale.value = current;
        for (const element of document.querySelectorAll("[data-i18n]")) {
            const key = element.dataset.i18n;
            const groupName = element.dataset.i18nGroup || ["controls", "layout", "main", "files", "preview", "validation", "history", "navigation"].find(name =>
                getGroup(fallback, name)[key] !== undefined);
            if (groupName) element.textContent = lookup(key, groupName);
        }
        for (const element of document.querySelectorAll("[data-i18n-placeholder]")) {
            element.placeholder = lookup(element.dataset.i18nPlaceholder, "controls");
        }
        for (const element of document.querySelectorAll("[data-i18n-aria-label]")) {
            element.setAttribute("aria-label", t(element.dataset.i18nAriaLabel, {}, ["navigation", "layout", "messages"].find(name => getGroup(fallback, name)[element.dataset.i18nAriaLabel] !== undefined) || "messages"));
        }
        for (const element of document.querySelectorAll("[data-i18n-title]")) {
            element.title = t(element.dataset.i18nTitle, {}, "navigation");
        }
    };
    const setLocale = code => {
        current = normalize(code);
        try { localStorage.setItem(storageKey, current); } catch {}
        translate();
        document.dispatchEvent(new CustomEvent("data-toolkit:locale-change", {detail: {locale: current}}));
    };
    window.DataToolkitI18n = Object.freeze({supported, fallback, getLocale: () => current, setLocale, group, t, translate});
})();
