// 控制台页面前端逻辑：角色控制 + 业务调用
(function () {
    const { request, requestFormData, clearSession } = window.ApiClient || {};

    function startDotsLoading(setText, prefix = "处理中") {
        let dots = 0;
        setText(`${prefix}...`);
        const timer = setInterval(() => {
            dots = (dots + 1) % 4;
            setText(`${prefix}${".".repeat(dots)}`);
        }, 350);
        return () => clearInterval(timer);
    }

    function setButtonLoading(btn, loading) {
        if (!btn) return;
        if (loading) {
            btn.disabled = true;
            btn.dataset.originalText = btn.textContent;
            btn.textContent = "处理中...";
        } else {
            btn.disabled = false;
            if (btn.dataset.originalText) btn.textContent = btn.dataset.originalText;
        }
    }

    function renderInfoCard(container, title, badgeText, entries) {
        if (!container) return;
        container.innerHTML = "";

        const card = document.createElement("div");
        card.className = "info-card";

        const h = document.createElement("h3");
        h.className = "card-title";
        h.textContent = title;

        if (badgeText) {
            const badge = document.createElement("span");
            badge.className = "card-badge";
            badge.textContent = badgeText;
            h.appendChild(badge);
        }

        const dl = document.createElement("dl");
        dl.className = "kv-list";

        (entries || []).forEach(({ label, value }) => {
            const dt = document.createElement("dt");
            dt.textContent = label;
            const dd = document.createElement("dd");
            dd.textContent = value === null || value === undefined || value === "" ? "-" : String(value);
            dl.appendChild(dt);
            dl.appendChild(dd);
        });

        card.appendChild(h);
        card.appendChild(dl);
        container.appendChild(card);
    }

    function appendInfoCard(container, title, badgeText, entries) {
        if (!container) return;
        const card = document.createElement("div");
        card.className = "info-card";

        const h = document.createElement("h3");
        h.className = "card-title";
        h.textContent = title;

        if (badgeText) {
            const badge = document.createElement("span");
            badge.className = "card-badge";
            badge.textContent = badgeText;
            h.appendChild(badge);
        }

        const dl = document.createElement("dl");
        dl.className = "kv-list";

        (entries || []).forEach(({ label, value }) => {
            const dt = document.createElement("dt");
            dt.textContent = label;
            const dd = document.createElement("dd");
            dd.textContent = value === null || value === undefined || value === "" ? "-" : String(value);
            dl.appendChild(dt);
            dl.appendChild(dd);
        });

        card.appendChild(h);
        card.appendChild(dl);
        container.appendChild(card);
    }

    function getUserInfoFromStorage() {
        try {
            const raw = localStorage.getItem("user_info");
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            return null;
        }
    }

    function ensureLoggedIn() {
        const token = localStorage.getItem("access_token");
        if (!token) {
            window.location.href = "index.html";
            return false;
        }
        return true;
    }

    function setupSidebarUser(user) {
        const nameEl = document.getElementById("sidebarUsername");
        const roleEl = document.getElementById("sidebarRole");
        if (!user || !nameEl || !roleEl) return;
        nameEl.textContent = user.username || "";
        const roleMap = { admin: "管理员", driver: "司机", customer: "客户" };
        roleEl.textContent = roleMap[user.role] || user.role || "";
    }

    function setupRoleVisibility(user) {
        const role = user?.role;
        // data-roles 控制：逗号分隔，如 data-roles="admin,driver"
        document.querySelectorAll("[data-roles]").forEach(el => {
            const raw = el.getAttribute("data-roles") || "";
            const allowed = raw
                .split(",")
                .map(s => s.trim())
                .filter(Boolean);
            if (!allowed.length) return;

            if (allowed.includes(role)) {
                el.classList.remove("hidden");
            } else {
                el.classList.add("hidden");
            }
        });
    }

    function setupMenuSwitching() {
        const buttons = document.querySelectorAll(".menu-item");
        const sections = document.querySelectorAll(".content-section");
        buttons.forEach(btn => {
            btn.addEventListener("click", () => {
                const target = btn.getAttribute("data-target");
                buttons.forEach(b => b.classList.remove("active"));
                sections.forEach(sec => sec.classList.remove("active"));
                btn.classList.add("active");
                const section = document.getElementById(target);
                if (section) section.classList.add("active");
            });
        });

        // 默认激活：选择第一个未被隐藏的菜单项
        const first = Array.from(buttons).find(btn => !btn.classList.contains("hidden"));
        if (first) {
            const target = first.getAttribute("data-target");
            buttons.forEach(b => b.classList.remove("active"));
            sections.forEach(sec => sec.classList.remove("active"));
            first.classList.add("active");
            const section = document.getElementById(target);
            if (section) section.classList.add("active");
        }
    }

    function setupLogout() {
        const btn = document.getElementById("logoutBtn");
        if (!btn) return;
        btn.addEventListener("click", () => {
            clearSession();
            window.location.href = "index.html";
        });
    }

    // ========== 订单模块 ==========
    async function handleOrderCreate(e) {
        e.preventDefault();
        if (!request) return;
        const form = e.target;
        const formData = new FormData(form);
        const body = {};
        formData.forEach((v, k) => {
            body[k] = v;
        });
        body.goods_quantity = Number(body.goods_quantity || 1);

        const msgEl = document.getElementById("orderCreateMsg");
        if (msgEl) msgEl.textContent = "";
        try {
            const data = await request("/api/v1/order/create", {
                method: "POST",
                body: JSON.stringify(body)
            });
            if (msgEl) msgEl.textContent = `订单创建成功：订单号 ${data.order_no}`;
            form.reset();
            await loadOrderList({ page: 1, page_size: 20 });
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "订单创建失败";
        }
    }

    async function loadOrderList(params = {}) {
        if (!request) return;
        const query = new URLSearchParams();
        Object.entries(params).forEach(([k, v]) => {
            if (v !== "" && v !== null && v !== undefined) {
                query.append(k, v);
            }
        });

        const tableBody = document.querySelector("#orderTable tbody");
        if (!tableBody) return;
        tableBody.innerHTML = "";

        try {
            const data = await request(`/api/v1/order/query?${query.toString()}`, {
                method: "GET"
            });

            (data.data || []).forEach(row => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${row.order_no ?? ""}</td>
                    <td>${row.receiver_name || ""}</td>
                    <td>${row.receiver_phone || ""}</td>
                    <td>${row.receiver_address || ""}</td>
                    <td>${row.order_status}</td>
                    <td>${row.driver_id || ""}</td>
                    <td>
                        <button type="button" class="btn secondary btn-order-detail" data-order-no="${row.order_no}">详情</button>
                    </td>
                `;
                tableBody.appendChild(tr);
            });
        } catch (err) {
            tableBody.innerHTML = `<tr><td colspan="7">${err.message || "加载订单失败"}</td></tr>`;
        }
    }

    async function handleOrderDetailSubmit(e) {
        e.preventDefault();
        if (!request) return;
        const form = e.target;
        const fd = new FormData(form);
        const order_no = fd.get("order_no");

        const box = document.getElementById("orderDetailResult");
        if (box) box.innerHTML = "";
        if (!order_no) {
            if (box) box.innerHTML = `<div class="loading-text muted">请输入订单号</div>`;
            return;
        }

        try {
            const data = await request(`/api/v1/order/detail/${order_no}`, {
                method: "GET"
            });
            renderInfoCard(
                box,
                "订单详情",
                data.order_status ? `状态：${data.order_status}` : "",
                [
                    { label: "订单号", value: data.order_no },
                    { label: "订单ID", value: data.id },
                    { label: "发件人", value: data.sender_name },
                    { label: "发件手机号", value: data.sender_phone },
                    { label: "发件地址", value: data.sender_address },
                    { label: "收件人", value: data.receiver_name },
                    { label: "收件手机号", value: data.receiver_phone },
                    { label: "收件地址", value: data.receiver_address },
                    { label: "货物类型", value: data.goods_type },
                    { label: "货物数量", value: data.goods_quantity },
                    { label: "司机ID", value: data.driver_id },
                    { label: "仓库ID", value: data.warehouse_id },
                    { label: "创建人ID", value: data.create_user_id },
                    { label: "创建时间", value: data.create_time },
                    { label: "更新时间", value: data.update_time }
                ]
            );
        } catch (err) {
            if (box) box.innerHTML = `<div class="loading-text">${err.message || "查询订单详情失败"}</div>`;
        }
    }

    function toggleOrderStatusDriverGroup() {
        const statusSelect = document.querySelector("#orderStatusForm select[name=\"order_status\"]");
        const group = document.getElementById("orderStatusDriverGroup");
        if (!statusSelect || !group) return;

        const isDelivering = statusSelect.value === "delivering";
        if (isDelivering) {
            group.classList.remove("hidden");
        } else {
            group.classList.add("hidden");
        }
    }

    async function handleOrderStatusUpdate(e) {
        e.preventDefault();
        if (!request) return;

        const form = e.target;
        const fd = new FormData(form);
        const order_id = Number(fd.get("order_id"));
        const order_status = fd.get("order_status");
        const driver_id_raw = fd.get("driver_id");

        const msgEl = document.getElementById("orderStatusMsg");
        if (msgEl) msgEl.textContent = "";

        if (!order_id || !order_status) {
            if (msgEl) msgEl.textContent = "请填写订单ID与订单状态";
            return;
        }

        const body = { order_status };
        if (order_status === "delivering") {
            const driver_id = driver_id_raw ? Number(driver_id_raw) : null;
            if (!driver_id) {
                if (msgEl) msgEl.textContent = "订单状态为 delivering 时必须填写司机ID";
                return;
            }
            body.driver_id = driver_id;
        }

        try {
            const data = await request(`/api/v1/order/status/${order_id}`, {
                method: "PUT",
                body: JSON.stringify(body)
            });
            if (msgEl) msgEl.textContent = `更新成功：订单号 ${data.order_no} → ${data.order_status}`;
            await loadOrderList({ page: 1, page_size: 20 });
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "更新订单状态失败";
        }
    }

    function setupOrderModule() {
        const createForm = document.getElementById("orderCreateForm");
        if (createForm) createForm.addEventListener("submit", handleOrderCreate);

        const queryForm = document.getElementById("orderQueryForm");
        if (queryForm) {
            queryForm.addEventListener("submit", (e) => {
                e.preventDefault();
                const fd = new FormData(queryForm);
                loadOrderList({
                    order_no: fd.get("order_no") || "",
                    order_status: fd.get("order_status") || "",
                    page: 1,
                    page_size: 20
                });
            });
        }

        const detailForm = document.getElementById("orderDetailForm");
        if (detailForm) detailForm.addEventListener("submit", handleOrderDetailSubmit);

        const statusForm = document.getElementById("orderStatusForm");
        if (statusForm) {
            statusForm.addEventListener("submit", handleOrderStatusUpdate);
            const statusSelect = statusForm.querySelector("select[name=\"order_status\"]");
            if (statusSelect) statusSelect.addEventListener("change", toggleOrderStatusDriverGroup);
            toggleOrderStatusDriverGroup();
        }

        const orderTable = document.getElementById("orderTable");
        if (orderTable) {
            orderTable.addEventListener("click", (e) => {
                const btn = e.target.closest(".btn-order-detail");
                if (!btn) return;
                const orderNo = btn.getAttribute("data-order-no");
                const input = document.querySelector("#orderDetailForm input[name=\"order_no\"]");
                if (input) input.value = orderNo || "";
                const form = document.getElementById("orderDetailForm");
                if (form) form.requestSubmit();
            });
        }

        loadOrderList({ page: 1, page_size: 20 }).then();
    }

    // ========== 仓库模块 ==========
    async function handleWarehouseCreate(e) {
        e.preventDefault();
        if (!request) return;
        const form = e.target;
        const fd = new FormData(form);
        const body = {
            warehouse_name: fd.get("warehouse_name"),
            province: fd.get("province") || null,
            city: fd.get("city") || null,
            district: fd.get("district") || null,
            address: fd.get("address") || null,
            capacity_limit: Number(fd.get("capacity_limit")),
        };

        const manager_id_raw = fd.get("manager_id");
        if (manager_id_raw) body.manager_id = Number(manager_id_raw);

        const msgEl = document.getElementById("warehouseCreateMsg");
        if (msgEl) msgEl.textContent = "";

        try {
            const data = await request("/api/v1/warehouse/create", {
                method: "POST",
                body: JSON.stringify(body)
            });
            if (msgEl) msgEl.textContent = `仓库创建成功：${data.warehouse_name} (ID: ${data.id})`;
            form.reset();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "仓库创建失败";
        }
    }

    async function handleWarehouseUpdate(e) {
        e.preventDefault();
        if (!request) return;
        const form = e.target;
        const fd = new FormData(form);
        const body = {
            id: Number(fd.get("id")),
            warehouse_name: fd.get("warehouse_name"),
            province: fd.get("province") || null,
            city: fd.get("city") || null,
            district: fd.get("district") || null,
            address: fd.get("address") || null,
            capacity_limit: Number(fd.get("capacity_limit")),
        };

        const manager_id_raw = fd.get("manager_id");
        if (manager_id_raw) body.manager_id = Number(manager_id_raw);

        const msgEl = document.getElementById("warehouseUpdateMsg");
        if (msgEl) msgEl.textContent = "";

        try {
            const data = await request("/api/v1/warehouse/update", {
                method: "POST",
                body: JSON.stringify(body)
            });
            if (msgEl) msgEl.textContent = `仓库更新成功：${data.warehouse_name} (ID: ${data.id})`;
            form.reset();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "仓库更新失败";
        }
    }

    async function handleWarehouseDetailQuery(e) {
        e.preventDefault();
        if (!request) return;
        const form = e.target;
        const fd = new FormData(form);
        const warehouse_id = fd.get("warehouse_id");

        const box = document.getElementById("warehouseDetailResult");
        if (box) box.innerHTML = "";

        if (!warehouse_id) {
            if (box) box.innerHTML = `<div class="loading-text muted">请输入仓库ID</div>`;
            return;
        }

        try {
            const data = await request(`/api/v1/warehouse/detail/${warehouse_id}`, {
                method: "GET"
            });
            const addr = `${data.province || ""}${data.city || ""}${data.district || ""}${data.address || ""}` || "-";
            renderInfoCard(
                box,
                "仓库详情",
                data.stock_warning ? "预警" : "正常",
                [
                    { label: "仓库ID", value: data.id },
                    { label: "仓库名称", value: data.warehouse_name },
                    { label: "地址", value: addr },
                    { label: "容量上限", value: data.capacity_limit },
                    { label: "当前库存", value: data.current_stock },
                    { label: "是否预警", value: data.stock_warning ? "是" : "否" },
                    { label: "管理员ID", value: data.manager_id },
                    { label: "管理员姓名", value: data.manager_name },
                    { label: "创建时间", value: data.create_time },
                    { label: "更新时间", value: data.update_time }
                ]
            );
        } catch (err) {
            if (box) box.innerHTML = `<div class="loading-text">${err.message || "查询仓库详情失败"}</div>`;
        }
    }

    async function handleStockQuery(e) {
        e.preventDefault();
        if (!request) return;
        const form = e.target;
        const fd = new FormData(form);

        const warningInput = form.querySelector('input[name="warning_only"]');
        const warning_only = warningInput ? !!warningInput.checked : false;

        const warehouse_id_raw = fd.get("warehouse_id");
        const body = {
            warning_only,
            page: Number(fd.get("page") || 1),
            page_size: Number(fd.get("page_size") || 10)
        };
        if (warehouse_id_raw) body.warehouse_id = Number(warehouse_id_raw);

        const tbody = document.querySelector("#stockTable tbody");
        if (!tbody) return;
        tbody.innerHTML = "";

        try {
            const data = await request("/api/v1/warehouse/stock/query", {
                method: "POST",
                body: JSON.stringify(body)
            });

            (data.data || []).forEach(item => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${item.id ?? ""}</td>
                    <td>${item.warehouse_name || ""}</td>
                    <td>${item.current_stock ?? ""}</td>
                    <td>${item.capacity_limit ?? ""}</td>
                    <td>${item.stock_warning ? "是" : "否"}</td>
                    <td>${item.manager_name || ""}</td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="6">${err.message || "库存查询失败"}</td></tr>`;
        }
    }

    async function handleWarehouseInbound(e) {
        e.preventDefault();
        if (!request) return;
        const form = e.target;
        const fd = new FormData(form);

        const body = {
            warehouse_id: Number(fd.get("warehouse_id")),
            goods_quantity: Number(fd.get("goods_quantity"))
        };

        const order_id_raw = fd.get("order_id");
        if (order_id_raw) body.order_id = Number(order_id_raw);

        const goods_type = fd.get("goods_type");
        if (goods_type) body.goods_type = goods_type;

        const msgEl = document.getElementById("warehouseInboundMsg");
        if (msgEl) msgEl.textContent = "";

        try {
            const data = await request("/api/v1/warehouse/inbound", {
                method: "POST",
                body: JSON.stringify(body)
            });
            if (msgEl) msgEl.textContent = `入库成功：记录ID ${data.id}`;
            form.reset();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "入库失败";
        }
    }

    async function handleWarehouseOutbound(e) {
        e.preventDefault();
        if (!request) return;
        const form = e.target;
        const fd = new FormData(form);

        const body = {
            warehouse_id: Number(fd.get("warehouse_id")),
            goods_quantity: Number(fd.get("goods_quantity"))
        };

        const order_id_raw = fd.get("order_id");
        if (order_id_raw) body.order_id = Number(order_id_raw);

        const goods_type = fd.get("goods_type");
        if (goods_type) body.goods_type = goods_type;

        const msgEl = document.getElementById("warehouseOutboundMsg");
        if (msgEl) msgEl.textContent = "";

        try {
            const data = await request("/api/v1/warehouse/outbound", {
                method: "POST",
                body: JSON.stringify(body)
            });
            if (msgEl) msgEl.textContent = `出库成功：记录ID ${data.id}`;
            form.reset();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "出库失败";
        }
    }

    function setupWarehouseModule(user) {
        const stockForm = document.getElementById("stockQueryForm");
        if (stockForm) stockForm.addEventListener("submit", handleStockQuery);

        const detailForm = document.getElementById("warehouseDetailForm");
        if (detailForm) detailForm.addEventListener("submit", handleWarehouseDetailQuery);

        if (!user || user.role !== "admin") return;

        const createForm = document.getElementById("warehouseCreateForm");
        if (createForm) createForm.addEventListener("submit", handleWarehouseCreate);

        const updateForm = document.getElementById("warehouseUpdateForm");
        if (updateForm) updateForm.addEventListener("submit", handleWarehouseUpdate);

        const inboundForm = document.getElementById("warehouseInboundForm");
        if (inboundForm) inboundForm.addEventListener("submit", handleWarehouseInbound);

        const outboundForm = document.getElementById("warehouseOutboundForm");
        if (outboundForm) outboundForm.addEventListener("submit", handleWarehouseOutbound);
    }

    // ========== 配送模块 ==========
    function getTaskOperationBtnColspan() {
        // 任务表：8列
        return 8;
    }

    async function loadDeliveryTasks(params = {}) {
        if (!request) return;

        const tableBody = document.querySelector("#deliveryTaskTable tbody");
        if (!tableBody) return;
        tableBody.innerHTML = "";

        const body = {
            order_no: params.order_no || undefined,
            task_status: params.task_status || undefined,
            page: Number(params.page || 1),
            page_size: Number(params.page_size || 10)
        };

        // 去掉 undefined，保证请求更贴合 schema 的 Optional 字段
        Object.keys(body).forEach(k => {
            if (body[k] === undefined) delete body[k];
        });

        try {
            const data = await request("/api/v1/delivery/task/query", {
                method: "POST",
                body: JSON.stringify(body)
            });

            (data.data || []).forEach(task => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${task.id ?? ""}</td>
                    <td>${task.order_no ?? ""}</td>
                    <td>${task.order_id ?? ""}</td>
                    <td>${task.driver_id ?? ""}</td>
                    <td>${task.driver_name ?? ""}</td>
                    <td>${task.task_status ?? ""}</td>
                    <td>${task.delivery_notes ?? ""}</td>
                    <td>
                        <button type="button" class="btn secondary btn-track-view" data-task-id="${task.id}">查看轨迹</button>
                        <button type="button" class="btn secondary btn-task-set-status" data-task-id="${task.id}">填入状态</button>
                    </td>
                `;
                tableBody.appendChild(tr);
            });
        } catch (err) {
            tableBody.innerHTML = `<tr><td colspan="${getTaskOperationBtnColspan()}">${err.message || "任务查询失败"}</td></tr>`;
        }
    }

    async function handleDeliveryTaskQuery(e) {
        e.preventDefault();
        const form = e.target;
        const fd = new FormData(form);
        await loadDeliveryTasks({
            order_no: fd.get("order_no") || "",
            task_status: fd.get("task_status") || "",
            page: Number(fd.get("page") || 1),
            page_size: Number(fd.get("page_size") || 10)
        });
    }

    async function handleDeliveryTaskStatusUpdate(e) {
        e.preventDefault();
        if (!request) return;

        const form = e.target;
        const fd = new FormData(form);
        const task_id = Number(fd.get("task_id"));
        const task_status = fd.get("task_status");
        const track_node = fd.get("track_node");
        const track_address_raw = (fd.get("track_address") || "").toString().trim();

        const msgEl = document.getElementById("deliveryTaskStatusMsg");
        if (msgEl) msgEl.textContent = "";

        if (!task_id || !task_status || !track_node) {
            if (msgEl) msgEl.textContent = "请填写任务ID/任务状态/轨迹节点";
            return;
        }

        const body = {
            task_id,
            task_status,
            track_node
        };
        if (track_address_raw) body.track_address = track_address_raw;

        try {
            const data = await request("/api/v1/delivery/task/status", {
                method: "POST",
                body: JSON.stringify(body)
            });
            if (msgEl) msgEl.textContent = `更新成功：任务ID ${data.id} → ${data.task_status}`;
            await loadDeliveryTasks();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "更新任务状态失败";
        }
    }

    async function handleDeliveryTrackCreate(e) {
        e.preventDefault();
        if (!request) return;

        const form = e.target;
        const fd = new FormData(form);
        const task_id = Number(fd.get("task_id"));
        const track_node = fd.get("track_node");
        const track_address_raw = (fd.get("track_address") || "").toString().trim();

        const msgEl = document.getElementById("deliveryTrackCreateMsg");
        if (msgEl) msgEl.textContent = "";

        const body = {
            task_id,
            track_node
        };
        if (track_address_raw) body.track_address = track_address_raw;

        try {
            const data = await request("/api/v1/delivery/track/create", {
                method: "POST",
                body: JSON.stringify(body)
            });
            if (msgEl) msgEl.textContent = `轨迹创建成功：ID ${data.id}`;
            const queryForm = document.getElementById("deliveryTrackQueryForm");
            if (queryForm) {
                const taskIdInput = queryForm.querySelector('input[name="task_id"]');
                if (taskIdInput) taskIdInput.value = task_id;
                await requestDeliveryTrackQuery();
            }
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "创建轨迹失败";
        }
    }

    async function requestDeliveryTrackQuery() {
        if (!request) return;
        const form = document.getElementById("deliveryTrackQueryForm");
        if (!form) return;
        const fd = new FormData(form);
        const task_id = Number(fd.get("task_id"));
        const box = document.getElementById("deliveryTrackResult");
        if (box) box.innerHTML = "";

        if (!task_id) {
            if (box) box.innerHTML = `<div class="loading-text muted">请输入任务ID</div>`;
            return;
        }

        try {
            const data = await request(`/api/v1/delivery/track/${task_id}`, {
                method: "GET"
            });
            if (box) {
                const tracks = data.tracks || [];
                if (!tracks.length) {
                    box.innerHTML = `<div class="loading-text muted">暂无轨迹记录</div>`;
                    return;
                }
                appendInfoCard(
                    box,
                    "轨迹汇总",
                    `任务ID：${data.task_id}`,
                    [{ label: "轨迹条数", value: tracks.length }]
                );
                tracks.forEach((t, idx) => {
                    appendInfoCard(
                        box,
                        `轨迹节点 #${idx + 1}`,
                        t.track_node || "",
                        [
                            { label: "轨迹ID", value: t.id },
                            { label: "任务ID", value: t.task_id },
                            { label: "轨迹节点", value: t.track_node },
                            { label: "轨迹时间", value: t.track_time },
                            { label: "轨迹地址", value: t.track_address },
                            { label: "司机姓名", value: t.driver_name }
                        ]
                    );
                });
            }
        } catch (err) {
            if (box) box.innerHTML = `<div class="loading-text">${err.message || "查询轨迹失败"}</div>`;
        }
    }

    async function handleDeliveryTrackQuery(e) {
        e.preventDefault();
        await requestDeliveryTrackQuery();
    }

    async function handleDriverEfficiencyBatch(e) {
        e.preventDefault();
        if (!request) return;

        const form = e.target;
        const fd = new FormData(form);
        const days = Number(fd.get("days") || 30);
        const msgEl = document.getElementById("driverEfficiencyBatchMsg");
        if (msgEl) msgEl.textContent = "";

        try {
            const data = await request(`/api/v1/delivery/driver/efficiency/batch?days=${days}`, {
                method: "POST"
            });
            if (msgEl) msgEl.textContent = data.message || "更新完成";
            await loadDeliveryTasks();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "批量更新效率失败";
        }
    }

    async function handleSmartAssign(e) {
        e.preventDefault();
        if (!request) return;

        const fd = new FormData(e.target);
        const order_id = Number(fd.get("order_id"));
        const msgEl = document.getElementById("smartAssignMsg");
        if (msgEl) msgEl.textContent = "";

        if (!order_id) {
            if (msgEl) msgEl.textContent = "请填写订单ID";
            return;
        }

        try {
            const data = await request(`/api/v1/delivery/task/smart-assign?order_id=${order_id}`, {
                method: "POST"
            });
            if (msgEl) msgEl.textContent = `智能分配成功：任务ID ${data.id}，司机ID ${data.driver_id}`;
            await loadDeliveryTasks();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "智能分配失败";
        }
    }

    async function handleDriverExtQuery(e, user) {
        e.preventDefault();
        if (!request) return;

        const form = e.target;
        const fd = new FormData(form);
        let user_id_raw = fd.get("user_id");
        if (!user_id_raw && user?.role === "driver") {
            user_id_raw = user.id;
        }

        const user_id = Number(user_id_raw);
        const box = document.getElementById("driverExtQueryResult");
        if (box) box.innerHTML = "";

        if (!user_id) {
            if (box) box.innerHTML = `<div class="loading-text muted">请填写司机用户ID</div>`;
            return;
        }

        try {
            const data = await request(`/api/v1/delivery/driver/ext/${user_id}`, {
                method: "GET"
            });
            renderInfoCard(
                box,
                "司机扩展信息",
                data.username || "",
                [
                    { label: "扩展ID", value: data.id },
                    { label: "司机用户ID", value: data.user_id },
                    { label: "用户名", value: data.username },
                    { label: "真实姓名", value: data.real_name },
                    { label: "车牌号", value: data.car_no },
                    { label: "常配送区域", value: data.delivery_area },
                    { label: "待完成任务数", value: data.task_count },
                    { label: "配送效率(%)", value: data.efficiency }
                ]
            );
        } catch (err) {
            if (box) box.innerHTML = `<div class="loading-text">${err.message || "查询司机扩展信息失败"}</div>`;
        }
    }

    async function handleDriverExtCreate(e) {
        e.preventDefault();
        if (!request) return;

        const form = e.target;
        const fd = new FormData(form);
        const body = {
            user_id: Number(fd.get("user_id")),
            car_no: fd.get("car_no"),
            delivery_area: fd.get("delivery_area") || null
        };

        const msgEl = document.getElementById("driverExtCreateMsg");
        if (msgEl) msgEl.textContent = "";

        try {
            const data = await request("/api/v1/delivery/driver/ext/create", {
                method: "POST",
                body: JSON.stringify(body)
            });
            if (msgEl) msgEl.textContent = `创建成功：ID ${data.id} (user_id=${data.user_id})`;
            form.reset();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "创建司机扩展信息失败";
        }
    }

    async function handleDriverExtUpdate(e) {
        e.preventDefault();
        if (!request) return;

        const form = e.target;
        const fd = new FormData(form);
        const body = {
            id: Number(fd.get("id")),
            user_id: Number(fd.get("user_id")),
            car_no: fd.get("car_no"),
            delivery_area: fd.get("delivery_area") || null
        };

        const msgEl = document.getElementById("driverExtUpdateMsg");
        if (msgEl) msgEl.textContent = "";

        try {
            const data = await request("/api/v1/delivery/driver/ext/update", {
                method: "POST",
                body: JSON.stringify(body)
            });
            if (msgEl) msgEl.textContent = `更新成功：ID ${data.id}`;
            form.reset();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "更新司机扩展信息失败";
        }
    }

    async function handleDeliveryTaskAssign(e) {
        e.preventDefault();
        if (!request) return;
        const fd = new FormData(e.target);
        const order_id = Number(fd.get("order_id"));
        const driver_id = Number(fd.get("driver_id"));

        const msgEl = document.getElementById("deliveryTaskAssignMsg");
        if (msgEl) msgEl.textContent = "";

        try {
            const data = await request("/api/v1/delivery/task/assign", {
                method: "POST",
                body: JSON.stringify({ order_id, driver_id })
            });
            if (msgEl) msgEl.textContent = `分配成功：任务ID ${data.id}，司机ID ${data.driver_id}`;
            await loadDeliveryTasks();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "分配任务失败";
        }
    }

    function setupDeliveryModule(user) {
        const queryForm = document.getElementById("deliveryTaskQueryForm");
        if (queryForm) queryForm.addEventListener("submit", handleDeliveryTaskQuery);

        const assignForm = document.getElementById("deliveryTaskAssignForm");
        if (assignForm) assignForm.addEventListener("submit", handleDeliveryTaskAssign);

        const statusForm = document.getElementById("deliveryTaskStatusForm");
        if (statusForm) statusForm.addEventListener("submit", handleDeliveryTaskStatusUpdate);

        const trackCreateForm = document.getElementById("deliveryTrackCreateForm");
        if (trackCreateForm) trackCreateForm.addEventListener("submit", handleDeliveryTrackCreate);

        const trackQueryForm = document.getElementById("deliveryTrackQueryForm");
        if (trackQueryForm) trackQueryForm.addEventListener("submit", handleDeliveryTrackQuery);

        const efficiencyForm = document.getElementById("driverEfficiencyBatchForm");
        if (efficiencyForm) efficiencyForm.addEventListener("submit", handleDriverEfficiencyBatch);

        const smartAssignForm = document.getElementById("smartAssignForm");
        if (smartAssignForm) smartAssignForm.addEventListener("submit", handleSmartAssign);

        const driverExtQueryForm = document.getElementById("driverExtQueryForm");
        if (driverExtQueryForm) driverExtQueryForm.addEventListener("submit", (e) => handleDriverExtQuery(e, user));

        const driverExtCreateForm = document.getElementById("driverExtCreateForm");
        if (driverExtCreateForm) driverExtCreateForm.addEventListener("submit", handleDriverExtCreate);

        const driverExtUpdateForm = document.getElementById("driverExtUpdateForm");
        if (driverExtUpdateForm) driverExtUpdateForm.addEventListener("submit", handleDriverExtUpdate);

        const tbody = document.querySelector("#deliveryTaskTable tbody");
        if (tbody) {
            tbody.addEventListener("click", async (e) => {
                const btnTrack = e.target.closest(".btn-track-view");
                if (btnTrack) {
                    const taskId = btnTrack.getAttribute("data-task-id");
                    const queryForm = document.getElementById("deliveryTrackQueryForm");
                    if (queryForm) {
                        const input = queryForm.querySelector('input[name="task_id"]');
                        if (input) input.value = taskId || "";
                    }
                    await requestDeliveryTrackQuery();
                    return;
                }

                const btnSetStatus = e.target.closest(".btn-task-set-status");
                if (btnSetStatus) {
                    const taskId = btnSetStatus.getAttribute("data-task-id");
                    const statusForm = document.getElementById("deliveryTaskStatusForm");
                    if (statusForm) {
                        const input = statusForm.querySelector('input[name="task_id"]');
                        if (input) input.value = taskId || "";
                    }
                }
            });
        }

        loadDeliveryTasks({ page: 1, page_size: 10 }).then();
    }

    // ========== 个人中心/AI模块 ==========
    async function loadProfileInfo() {
        if (!request) return;
        const box = document.getElementById("profileInfo");
        if (!box) return;
        try {
            const data = await request("/api/v1/user/info", {
                method: "GET"
            });
            box.textContent = `用户名：${data.username}，角色：${data.role}，手机号：${data.phone || "-"}，真实姓名：${data.real_name || "-"}`;
        } catch (err) {
            box.textContent = err.message || "加载个人信息失败";
        }
    }

    async function handleUpdateUserInfo(e) {
        e.preventDefault();
        if (!request) return;

        const form = e.target;
        const fd = new FormData(form);
        const phone_raw = (fd.get("phone") || "").toString().trim();
        const real_name_raw = (fd.get("real_name") || "").toString().trim();

        const msgEl = document.getElementById("updateUserInfoMsg");
        if (msgEl) msgEl.textContent = "";

        if (!phone_raw && !real_name_raw) {
            if (msgEl) msgEl.textContent = "请至少填写手机号或真实姓名";
            return;
        }

        const body = {};
        if (phone_raw) body.phone = phone_raw;
        if (real_name_raw) body.real_name = real_name_raw;

        try {
            const data = await request("/api/v1/user/info", {
                method: "PUT",
                body: JSON.stringify(body)
            });
            if (msgEl) msgEl.textContent = "保存成功";
            // 更新本地缓存的 user_info（便于角色显示等）
            try {
                localStorage.setItem("user_info", JSON.stringify(data || {}));
            } catch (e) {
                // ignore
            }
            await loadProfileInfo();
            form.reset();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "保存失败";
        }
    }

    async function handleResetPassword(e) {
        e.preventDefault();
        if (!request) return;

        const form = e.target;
        const fd = new FormData(form);
        const old_password = (fd.get("old_password") || "").toString();
        const new_password = (fd.get("new_password") || "").toString();

        const msgEl = document.getElementById("resetPasswordMsg");
        if (msgEl) msgEl.textContent = "";

        try {
            await request("/api/v1/user/reset-password", {
                method: "PUT",
                body: JSON.stringify({ old_password, new_password })
            });
            if (msgEl) msgEl.textContent = "密码重置成功";
            form.reset();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "重置失败";
        }
    }

    function setupProfileModule() {
        const updateForm = document.getElementById("updateUserInfoForm");
        if (updateForm) updateForm.addEventListener("submit", handleUpdateUserInfo);

        const resetForm = document.getElementById("resetPasswordForm");
        if (resetForm) resetForm.addEventListener("submit", handleResetPassword);
    }

    // ========== OCR 模块 ==========
    async function handleOcrRecognize(e) {
        e.preventDefault();
        if (!requestFormData) return;

        const form = e.target;
        const fd = new FormData(form);
        const msgEl = document.getElementById("ocrRecognizeMsg");
        if (msgEl) msgEl.textContent = "";

        const box = document.getElementById("ocrRecognizeResult");
        if (box) box.textContent = "";

        try {
            const data = await requestFormData("/api/v1/ocr/recognize", fd);
            if (msgEl) msgEl.textContent = data.message || "OCR识别完成";
            if (box) box.textContent = JSON.stringify(data, null, 2);
            form.reset();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "OCR识别失败";
        }
    }

    async function handleOcrRecordQuery(e) {
        e.preventDefault();
        if (!request) return;

        const form = e.target;
        const fd = new FormData(form);
        const record_id = Number(fd.get("record_id"));

        const box = document.getElementById("ocrRecordResult");
        if (box) box.innerHTML = "";

        if (!record_id) {
            if (box) box.innerHTML = `<div class="loading-text muted">请输入OCR记录ID</div>`;
            return;
        }

        try {
            const data = await request(`/api/v1/ocr/record/${record_id}`, { method: "GET" });
            const extract = (data && typeof data.extract_result === "object" && data.extract_result)
                ? data.extract_result
                : null;

            const keyMap = {
                sender_name: "发件人姓名",
                sender_phone: "发件人手机号",
                sender_province: "发件省",
                sender_city: "发件市",
                sender_district: "发件区/县",
                sender_address: "发件详细地址",

                receiver_name: "收件人姓名",
                receiver_phone: "收件人手机号",
                receiver_province: "收件省",
                receiver_city: "收件市",
                receiver_district: "收件区/县",
                receiver_address: "收件详细地址",

                goods_type: "货物类型",
                goods_quantity: "货物数量",
                warehouse_id: "仓库ID"
            };

            const orderedKeys = [
                "sender_name", "sender_phone",
                "sender_province", "sender_city", "sender_district", "sender_address",
                "receiver_name", "receiver_phone",
                "receiver_province", "receiver_city", "receiver_district", "receiver_address",
                "goods_type", "goods_quantity",
                "warehouse_id"
            ];

            function toDisplayValue(v) {
                if (v === null || v === undefined) return "-";
                if (typeof v === "string") {
                    const s = v.trim();
                    return s ? s : "-";
                }
                if (typeof v === "number" || typeof v === "boolean") return String(v);
                try {
                    return JSON.stringify(v);
                } catch (e) {
                    return String(v);
                }
            }

            let extractResultText = "-";
            if (extract) {
                const parts = [];
                // 先按固定顺序输出常见字段
                orderedKeys.forEach(k => {
                    if (Object.prototype.hasOwnProperty.call(extract, k)) {
                        parts.push(`${keyMap[k] || k}: ${toDisplayValue(extract[k])}`);
                    }
                });
                // 再输出未知字段
                Object.keys(extract).forEach(k => {
                    if (!orderedKeys.includes(k)) {
                        parts.push(`${keyMap[k] || k}: ${toDisplayValue(extract[k])}`);
                    }
                });
                extractResultText = parts.length ? parts.join("；") : "-";
            }

            renderInfoCard(
                box,
                "OCR识别记录",
                `记录ID：${record_id}`,
                [
                    { label: "OCR记录ID", value: data.ocr_record_id ?? data.id ?? record_id },
                    { label: "识别文本", value: data.ocr_text },
                    { label: "提取结果", value: extractResultText },
                    { label: "自动创建订单ID", value: data.order_id },
                    { label: "处理结果", value: data.message }
                ]
            );
        } catch (err) {
            if (box) box.innerHTML = `<div class="loading-text">${err.message || "查询OCR记录失败"}</div>`;
        }
    }

    function setupOcrModule(user) {
        if (!user || user.role !== "admin") return;
        const form = document.getElementById("ocrRecognizeForm");
        if (form) form.addEventListener("submit", handleOcrRecognize);

        const query = document.getElementById("ocrRecordQueryForm");
        if (query) query.addEventListener("submit", handleOcrRecordQuery);
    }

    // ========== 智能SQL 模块 ==========
    async function handleSqlAgent(e) {
        e.preventDefault();
        if (!request) return;

        const form = e.target;
        const fd = new FormData(form);
        const question = (fd.get("question") || "").toString().trim();

        const msgEl = document.getElementById("sqlAgentMsg");
        if (msgEl) msgEl.textContent = "";

        const box = document.getElementById("sqlAgentResult");
        if (box) box.textContent = "";

        const submitBtn = form.querySelector('button[type="submit"]');
        setButtonLoading(submitBtn, true);
        const stopLoading = box ? startDotsLoading((t) => { box.textContent = t; }, "正在查询") : () => {};

        if (!question) {
            if (msgEl) msgEl.textContent = "请输入问题";
            stopLoading();
            setButtonLoading(submitBtn, false);
            return;
        }

        try {
            const data = await request("/api/v1/sql/agent", {
                method: "POST",
                body: JSON.stringify({ question })
            });
            if (msgEl) msgEl.textContent = "生成并查询完成";
            stopLoading();
            if (box) box.textContent = data.answer || "无回答";
            form.reset();
        } catch (err) {
            stopLoading();
            if (msgEl) msgEl.textContent = err.message || "智能SQL失败";
        } finally {
            setButtonLoading(submitBtn, false);
        }
    }

    function setupSqlModule(user) {
        if (!user || user.role !== "admin") return;
        const form = document.getElementById("sqlAgentForm");
        if (form) form.addEventListener("submit", handleSqlAgent);
    }

    // ========== FAQ/RAG 模块 ==========
    function appendChatMessage(question, answer, recordId) {
        const box = document.getElementById("faqChatHistory");
        if (!box) return;
        const item = document.createElement("div");
        item.className = "chat-item";
        item.innerHTML = `
            <div class="chat-q">你：${question}</div>
            <div class="chat-a">AI：${answer || ""}${recordId ? `（record_id: ${recordId}）` : ""}</div>
        `;
        box.appendChild(item);
    }

    async function postFaqChat(question) {
        // faq.py 中 chat 路径写法可能导致最终路径为 /api/v1/faqchat
        try {
            return await request("/api/v1/faqchat", {
                method: "POST",
                body: JSON.stringify({ question })
            });
        } catch (e) {
            // 兼容可能的另一种路径写法
            return await request("/api/v1/faq/chat", {
                method: "POST",
                body: JSON.stringify({ question })
            });
        }
    }

    async function handleFaqChat(e) {
        e.preventDefault();
        if (!request) return;

        const form = e.target;
        const fd = new FormData(form);
        const question = (fd.get("question") || "").toString().trim();
        if (!question) return;

        const submitBtn = form.querySelector('button[type="submit"]');
        setButtonLoading(submitBtn, true);

        const history = document.getElementById("faqChatHistory");
        const pendingId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
        if (history) {
            const item = document.createElement("div");
            item.className = "chat-item";
            item.dataset.pendingId = pendingId;
            item.innerHTML = `
                <div class="chat-q">你：${question}</div>
                <div class="chat-a">AI：正在思考...</div>
            `;
            history.appendChild(item);
        }

        let stop = null;
        const pendingEl = history ? history.querySelector(`.chat-item[data-pending-id="${pendingId}"] .chat-a`) : null;
        if (pendingEl) {
            stop = startDotsLoading((t) => { pendingEl.textContent = `AI：${t}`; }, "正在思考");
        }

        try {
            const data = await postFaqChat(question);
            if (stop) stop();
            const item = history ? history.querySelector(`.chat-item[data-pending-id="${pendingId}"]`) : null;
            if (item) {
                const a = item.querySelector(".chat-a");
                if (a) a.textContent = `AI：${data.answer || ""}（record_id: ${data.record_id}）`;
                item.removeAttribute("data-pending-id");
            } else {
                appendChatMessage(data.question || question, data.answer, data.record_id);
            }
            form.reset();
        } catch (err) {
            if (stop) stop();
            const item = history ? history.querySelector(`.chat-item[data-pending-id="${pendingId}"]`) : null;
            if (item) {
                const a = item.querySelector(".chat-a");
                if (a) a.textContent = `AI：${err.message || "RAG对话失败"}`;
                item.removeAttribute("data-pending-id");
            } else {
                appendChatMessage(question, err.message || "RAG对话失败", null);
            }
        } finally {
            setButtonLoading(submitBtn, false);
        }
    }

    async function handleFaqAdminUploadPdf(e) {
        e.preventDefault();
        if (!requestFormData) return;

        const form = e.target;
        const fd = new FormData(form);
        const msgEl = document.getElementById("faqAdminUploadMsg");
        if (msgEl) msgEl.textContent = "";
        const box = document.getElementById("faqAdminUploadResult");
        if (box) box.textContent = "";

        try {
            const data = await requestFormData("/api/v1/faq/admin/upload/pdf", fd);
            if (msgEl) msgEl.textContent = data.status === "success" ? "上传成功" : "上传完成";
            if (box) box.textContent = JSON.stringify(data, null, 2);
            form.reset();
        } catch (err) {
            if (msgEl) msgEl.textContent = err.message || "上传失败";
        }
    }

    function setupFaqModule(user) {
        const chatForm = document.getElementById("faqChatForm");
        if (chatForm) chatForm.addEventListener("submit", handleFaqChat);

        if (!user || user.role !== "admin") return;
        const uploadForm = document.getElementById("faqAdminUploadForm");
        if (uploadForm) uploadForm.addEventListener("submit", handleFaqAdminUploadPdf);
    }

    document.addEventListener("DOMContentLoaded", () => {
        if (!ensureLoggedIn()) return;
        const user = getUserInfoFromStorage();

        setupSidebarUser(user);
        setupRoleVisibility(user);
        setupMenuSwitching();
        setupLogout();

        setupOrderModule();
        setupWarehouseModule(user);
        setupDeliveryModule(user);
        setupOcrModule(user);
        setupSqlModule(user);
        setupFaqModule(user);
        setupProfileModule();

        loadProfileInfo().then();
    });
})();

