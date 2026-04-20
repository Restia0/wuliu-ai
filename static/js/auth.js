// 登录与注册页前端逻辑
(function () {
    const { request, setSession } = window.ApiClient || {};

    function $(id) {
        return document.getElementById(id);
    }

    async function handleLogin(e) {
        e.preventDefault();
        const username = $("username").value.trim();
        const password = $("password").value;
        const errorBox = $("loginError");
        if (!request) return;

        errorBox.textContent = "";
        try {
            const data = await request("/api/v1/user/login", {
                method: "POST",
                body: JSON.stringify({ username, password })
            });
            setSession(data.access_token, data.user_info);
            window.location.href = "dashboard.html";
        } catch (err) {
            errorBox.textContent = err.message || "登录失败";
        }
    }

    async function handleRegister(e) {
        e.preventDefault();
        const username = $("reg_username").value.trim();
        const password = $("reg_password").value;
        const phone = $("reg_phone").value.trim() || null;
        const real_name = $("reg_real_name").value.trim() || null;
        const role = $("reg_role").value;
        const errorBox = $("registerError");
        if (!request) return;

        errorBox.textContent = "";
        try {
            await request("/api/v1/user/register", {
                method: "POST",
                body: JSON.stringify({
                    username,
                    password,
                    phone,
                    real_name,
                    role
                })
            });

            // 注册成功后直接登录
            const loginResp = await request("/api/v1/user/login", {
                method: "POST",
                body: JSON.stringify({ username, password })
            });
            setSession(loginResp.access_token, loginResp.user_info);
            window.location.href = "dashboard.html";
        } catch (err) {
            errorBox.textContent = err.message || "注册失败";
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        const loginForm = $("loginForm");
        const registerForm = $("registerForm");
        if (loginForm) {
            loginForm.addEventListener("submit", handleLogin);
        }
        if (registerForm) {
            registerForm.addEventListener("submit", handleRegister);
        }
    });
})();

