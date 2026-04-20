// 通用前端请求工具：封装基础URL、token与错误处理
(function () {
    // 自动使用当前页面端口，避免后端端口非 8000 时请求失败
    const portPart = window.location.port ? `:${window.location.port}` : "";
    const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}${portPart}`;

    function getToken() {
        return localStorage.getItem("access_token") || "";
    }

    function setSession(token, userInfo) {
        localStorage.setItem("access_token", token);
        localStorage.setItem("user_info", JSON.stringify(userInfo || {}));
    }

    function clearSession() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_info");
    }

    async function request(path, options = {}) {
        const headers = options.headers || {};
        headers["Content-Type"] = "application/json";
        const token = getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        const resp = await fetch(`${API_BASE_URL}${path}`, {
            ...options,
            headers
        });

        let data;
        try {
            data = await resp.json();
        } catch (e) {
            data = null;
        }

        if (!resp.ok) {
            const msg = (data && data.detail) || resp.statusText || "请求失败";
            throw new Error(msg);
        }
        return data;
    }

    async function requestFormData(path, formData, options = {}) {
        const headers = options.headers || {};
        const token = getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        // 让浏览器自动设置 boundary；不要手动写 Content-Type
        const resp = await fetch(`${API_BASE_URL}${path}`, {
            ...options,
            method: options.method || "POST",
            headers,
            body: formData
        });

        let data;
        try {
            data = await resp.json();
        } catch (e) {
            data = null;
        }

        if (!resp.ok) {
            const msg = (data && data.detail) || resp.statusText || "请求失败";
            throw new Error(msg);
        }
        return data;
    }

    window.ApiClient = {
        API_BASE_URL,
        getToken,
        setSession,
        clearSession,
        request,
        requestFormData
    };
})();

