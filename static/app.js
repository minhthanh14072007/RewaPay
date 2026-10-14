"use strict";

const byId = (id) => document.getElementById(id);
const money = (value) =>
  new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 0 }).format(value) + " ₫";
const number = (value) =>
  new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 0 }).format(value);

let state;
let displayTransactions = [];
let toastTimer;

async function request(url, options = {}) {
  const response = await fetch(url, options);
  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new Error("Máy chủ trả về phản hồi không hợp lệ.");
  }
  if (!response.ok) throw new Error(payload.error || "Yêu cầu không thành công.");
  return payload;
}

function showToast(message, isError = false) {
  const toast = byId("toast");
  toast.textContent = message;
  toast.style.color = isError ? "#a14338" : "#285c3d";
  toast.style.borderColor = isError ? "#f0d4d0" : "#d5e9da";
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 3200);
}

function makeCell(text, className = "") {
  const cell = document.createElement("td");
  cell.textContent = text;
  if (className) cell.className = className;
  return cell;
}

function memberName(memberId) {
  return state.members.find((member) => member.id === memberId)?.name || memberId;
}

function renderTransactions() {
  const body = byId("transactions-body");
  body.replaceChildren();
  const members = new Map(state.members.map((member) => [member.id, member]));
  for (const transaction of displayTransactions) {
    const row = document.createElement("tr");
    row.append(makeCell(transaction.id, "transaction-id"));
    row.append(makeCell(members.get(transaction.member_id)?.name || transaction.member_id, "member-name"));
    row.append(makeCell(money(transaction.amount_vnd), "amount-cell"));
    row.append(makeCell(transaction.refunded || transaction.status !== "approved" ? "—" : money(transaction.cashback_vnd), "cashback-cell"));
    row.append(makeCell(transaction.refunded || transaction.status !== "approved" ? "—" : number(transaction.points)));

    const statusCell = document.createElement("td");
    const status = document.createElement("span");
    status.className = `status-pill ${transaction.refunded ? "refunded" : transaction.status}`;
    status.textContent = transaction.refunded ? "Đã hoàn" : transaction.status === "pending" ? "Chờ duyệt" : "Đã duyệt";
    statusCell.append(status);
    row.append(statusCell);

    const actionCell = document.createElement("td");
    if (transaction.status === "approved" && !transaction.refunded) {
      const refund = document.createElement("button");
      refund.type = "button";
      refund.className = "row-action";
      refund.textContent = "Hoàn";
      refund.setAttribute("aria-label", `Hoàn giao dịch ${transaction.id}`);
      refund.addEventListener("click", () => refundTransaction(transaction.id));
      actionCell.append(refund);
    }
    row.append(actionCell);
    body.append(row);
  }
  byId("transactions-empty").hidden = displayTransactions.length > 0;
  byId("table-footer").textContent =
    `${number(displayTransactions.length)} giao dịch hiển thị` +
    (byId("search-input").value.trim() ? " · Đang lọc theo mã giao dịch" : "");
}

function renderReviews() {
  const list = byId("review-list");
  list.replaceChildren();
  byId("review-count").textContent = number(state.summary.pending_count);
  const pending = state.pending_priority.slice(0, 3);
  if (!pending.length) {
    const empty = document.createElement("div");
    empty.className = "review-empty";
    empty.textContent = "Không có giao dịch chờ duyệt.";
    list.append(empty);
  } else {
    for (const transaction of pending) {
      const item = document.createElement("div");
      item.className = "review-item";
      const details = document.createElement("div");
      const id = document.createElement("strong");
      id.textContent = `${transaction.id} · ${memberName(transaction.member_id)}`;
      const category = document.createElement("small");
      category.textContent = transaction.category;
      details.append(id, category);
      const amount = document.createElement("span");
      amount.className = "review-amount";
      amount.textContent = money(transaction.amount_vnd);
      item.append(details, amount);
      list.append(item);
    }
  }
  byId("approve-fifo-button").disabled = !state.summary.pending_count;
  byId("approve-priority-button").disabled = !state.summary.pending_count;
}

function renderMembers() {
  const members = [...state.members].sort(
    (left, right) =>
      right.points_balance - left.points_balance ||
      right.cashback_vnd - left.cashback_vnd
  );
  const list = byId("member-list");
  list.replaceChildren();
  byId("member-total").textContent = `${number(members.length)} hội viên`;
  for (const [index, member] of members.entries()) {
    const row = document.createElement("div");
    row.className = "member-row";
    const rank = document.createElement("span");
    rank.className = "rank";
    rank.textContent = String(index + 1).padStart(2, "0");
    const details = document.createElement("div");
    details.className = "member-cell";
    const avatar = document.createElement("span");
    avatar.className = "member-avatar";
    avatar.textContent = member.name.split(/\s+/).at(-1).slice(0, 1);
    const label = document.createElement("span");
    const name = document.createElement("strong");
    name.textContent = member.name;
    const tier = document.createElement("small");
    tier.textContent = `${member.id} · Hạng ${member.tier}`;
    label.append(name, tier);
    details.append(avatar, label);
    const points = document.createElement("span");
    points.className = "member-points";
    points.textContent = `${number(member.points_balance)} điểm`;
    const cashback = document.createElement("span");
    cashback.className = "member-cashback";
    cashback.textContent = money(member.cashback_vnd);
    row.append(rank, details, points, cashback);
    list.append(row);
  }
}

function renderMemberSelects() {
  const selects = [byId("transaction-member"), byId("redeem-member")];
  for (const select of selects) {
    const previous = select.value;
    select.replaceChildren();
    for (const member of state.members) {
      const option = document.createElement("option");
      option.value = member.id;
      option.textContent = `${member.name} · ${member.id}`;
      select.append(option);
    }
    if (state.members.some((member) => member.id === previous)) select.value = previous;
  }
  updateRedemptionPreview();
}

function renderSummary() {
  byId("stat-cashback").textContent = money(state.summary.cashback_vnd);
  byId("stat-points").textContent = number(state.summary.points_available);
  byId("stat-transactions").textContent = number(state.summary.transaction_count);
  byId("stat-pending").textContent = number(state.summary.pending_count);
  byId("undo-button").disabled = !state.summary.can_undo;
  byId("undo-button").title = state.summary.can_undo
    ? "Hoàn tác thao tác gần nhất"
    : "Chưa có thao tác để hoàn tác";
}

async function refresh(sort = byId("sort-select").value) {
  const [freshState, sorted] = await Promise.all([
    request("/api/state"),
    request(`/api/transactions?sort=${encodeURIComponent(sort)}`),
  ]);
  state = freshState;
  byId("search-input").value = "";
  displayTransactions = sorted.transactions;
  renderSummary();
  renderTransactions();
  renderReviews();
  renderMembers();
  renderMemberSelects();
}

async function submitJson(url, data, successMessage) {
  try {
    await request(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    await refresh();
    showToast(successMessage);
    return true;
  } catch (error) {
    showToast(error.message, true);
    return false;
  }
}

async function refundTransaction(transactionId) {
  if (!window.confirm(`Hoàn giao dịch ${transactionId}? Điểm thưởng và hoàn tiền sẽ bị thu hồi.`)) return;
  await submitJson("/api/refunds", { transaction_id: transactionId }, `Đã hoàn giao dịch ${transactionId}.`);
}

function updateRedemptionPreview() {
  if (!state) return;
  const member = state.members.find((item) => item.id === byId("redeem-member").value);
  const points = Number(byId("redeem-points").value) || 0;
  byId("selected-balance").textContent = `${number(member?.points_balance || 0)} điểm`;
  byId("redeem-value").textContent = money(points * 100);
}

byId("transaction-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const amount = Number(byId("transaction-amount").value);
  if (!Number.isSafeInteger(amount)) {
    showToast("Số tiền phải là số nguyên VND hợp lệ.", true);
    return;
  }
  const saved = await submitJson(
    "/api/transactions",
    {
      member_id: byId("transaction-member").value,
      amount_vnd: amount,
      category: byId("transaction-category").value,
    },
    amount > 5_000_000
      ? "Đã ghi nhận. Giao dịch được chuyển vào hàng chờ duyệt."
      : "Đã ghi nhận giao dịch và cập nhật điểm thưởng."
  );
  if (saved) {
    byId("transaction-form").reset();
    byId("add-transaction").hidden = true;
  }
});

byId("redeem-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const points = Number(byId("redeem-points").value);
  if (!Number.isSafeInteger(points)) {
    showToast("Số điểm đổi phải là số nguyên.", true);
    return;
  }
  const redeemed = await submitJson(
    "/api/redemptions",
    { member_id: byId("redeem-member").value, points },
    `Đã đổi ${number(points)} điểm thành ${money(points * 100)}.`
  );
  if (redeemed) byId("redeem-points").value = "";
});

byId("search-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = byId("search-input").value.trim();
  if (!query) {
    await refresh();
    return;
  }
  try {
    const result = await request(`/api/transactions/search?id=${encodeURIComponent(query)}`);
    displayTransactions = [result.transaction];
    renderTransactions();
  } catch (error) {
    displayTransactions = [];
    renderTransactions();
    showToast(error.message, true);
  }
});

byId("sort-select").addEventListener("change", async (event) => {
  try {
    const result = await request(`/api/transactions?sort=${encodeURIComponent(event.target.value)}`);
    displayTransactions = result.transactions;
    renderTransactions();
  } catch (error) {
    showToast(error.message, true);
  }
});

byId("approve-fifo-button").addEventListener("click", () =>
  submitJson("/api/reviews/process", { strategy: "fifo" }, "Đã duyệt giao dịch đến trước."),
);
byId("approve-priority-button").addEventListener("click", () =>
  submitJson("/api/reviews/process", { strategy: "priority" }, "Đã duyệt giao dịch có giá trị cao nhất."),
);
byId("undo-button").addEventListener("click", async () => {
  try {
    await request("/api/undo", { method: "POST" });
    await refresh();
    showToast("Đã hoàn tác thao tác gần nhất.");
  } catch (error) {
    showToast(error.message, true);
  }
});
byId("nav-toggle").addEventListener("click", (event) => {
  const button = event.currentTarget;
  const expanded = button.getAttribute("aria-expanded") === "true";
  button.setAttribute("aria-expanded", String(!expanded));
  button.setAttribute(
    "aria-label",
    expanded ? "Hiện thanh điều hướng" : "Ẩn thanh điều hướng",
  );
  document.querySelector(".app-shell").classList.toggle("sidebar-collapsed", expanded);
});
byId("refresh-button").addEventListener("click", async () => {
  try {
    await refresh();
    showToast("Dữ liệu đã được làm mới.");
  } catch (error) {
    showToast(error.message, true);
  }
});
byId("new-transaction-button").addEventListener("click", () => {
  byId("add-transaction").hidden = false;
  byId("add-transaction").scrollIntoView({ behavior: "smooth", block: "center" });
});
byId("close-transaction-button").addEventListener("click", () => {
  byId("add-transaction").hidden = true;
});
byId("redeem-member").addEventListener("change", updateRedemptionPreview);
byId("redeem-points").addEventListener("input", updateRedemptionPreview);
byId("notice-close").addEventListener("click", () => {
  document.querySelector(".notice").hidden = true;
});

const chatMessages = byId("chat-messages");
const chatCustomers = [
  {
    id: "customer-1",
    name: "Nguyễn Minh Anh",
    preview: "Điểm thưởng của tôi được tính thế nào ạ?",
    time: "09:42",
    messages: [
      { sender: "customer", text: "Chào shop, điểm thưởng của tôi được tính như thế nào ạ?" },
      { sender: "operator", text: "Dạ, mỗi 10.000 ₫ giao dịch được duyệt sẽ tích lũy 1 điểm ạ." },
      { sender: "customer", text: "Nếu hoàn giao dịch thì điểm có bị trừ không?" },
      { sender: "operator", text: "Dạ có, hệ thống sẽ thu hồi điểm của giao dịch đó. Nếu điểm đã được sử dụng thì yêu cầu hoàn sẽ bị từ chối trong bản demo." },
    ],
  },
  {
    id: "customer-2",
    name: "Trần Quốc Bảo",
    preview: "Tôi muốn kiểm tra giao dịch GD0004.",
    time: "09:18",
    messages: [
      { sender: "customer", text: "Chào bạn, tôi muốn kiểm tra giao dịch GD0004." },
      { sender: "operator", text: "Dạ, giao dịch đã được duyệt. Đây là thông tin minh họa trong bản demo ạ." },
    ],
  },
  {
    id: "customer-3",
    name: "Lê Thu Hà",
    preview: "Đổi điểm cần tối thiểu bao nhiêu?",
    time: "Hôm qua",
    messages: [
      { sender: "customer", text: "Đổi điểm cần tối thiểu bao nhiêu vậy shop?" },
      { sender: "operator", text: "Dạ, tối thiểu 100 điểm và số điểm đổi cần là bội số của 100 ạ." },
    ],
  },
];

function addChatMessage(sender, text) {
  const message = document.createElement("div");
  message.className = `chat-message ${sender}`;
  const author = document.createElement("strong");
  author.className = "chat-message-author";
  author.textContent = sender === "customer" ? "Khách hàng" : "Bạn · Nhân viên";
  const content = document.createElement("span");
  content.textContent = text;
  const time = document.createElement("time");
  time.dateTime = new Date().toISOString();
  time.textContent = new Intl.DateTimeFormat("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date());
  message.append(author, content, time);
  chatMessages.append(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderChatCustomers() {
  const list = byId("chat-customer-list");
  list.replaceChildren();
  for (const customer of chatCustomers) {
    const button = document.createElement("button");
    button.className = "chat-customer";
    button.type = "button";
    button.setAttribute("aria-label", `Mở cuộc trò chuyện với ${customer.name}`);
    const avatar = document.createElement("span");
    avatar.className = "chat-customer-avatar";
    avatar.textContent = customer.name.split(/\s+/).map((part) => part[0]).slice(-2).join("");
    const info = document.createElement("span");
    info.className = "chat-customer-info";
    const name = document.createElement("strong");
    name.textContent = customer.name;
    const preview = document.createElement("small");
    preview.textContent = customer.preview;
    info.append(name, preview);
    const time = document.createElement("span");
    time.className = "chat-customer-time";
    time.textContent = customer.time;
    button.append(avatar, info, time);
    button.addEventListener("click", () => openCustomerConversation(customer));
    list.append(button);
  }
}

function openCustomerConversation(customer) {
  byId("chat-customer-list").hidden = true;
  byId("chat-conversation").hidden = false;
  byId("chat-back").hidden = false;
  byId("chat-title").textContent = customer.name;
  byId("chat-subtitle").textContent = "Cuộc trò chuyện mô phỏng";
  chatMessages.replaceChildren();
  for (const message of customer.messages) addChatMessage(message.sender, message.text);
  byId("chat-input").focus();
}

function openChat() {
  const panel = byId("chat-panel");
  panel.hidden = false;
  byId("chat-launcher").setAttribute("aria-expanded", "true");
  byId("chat-title").textContent = "Tin nhắn khách hàng";
  byId("chat-subtitle").textContent = `${chatCustomers.length} cuộc trò chuyện · Mô phỏng`;
  byId("chat-customer-list").hidden = false;
  byId("chat-conversation").hidden = true;
  byId("chat-back").hidden = true;
}

function closeChat() {
  byId("chat-panel").hidden = true;
  byId("chat-launcher").setAttribute("aria-expanded", "false");
}

byId("chat-launcher").addEventListener("click", () => {
  if (byId("chat-panel").hidden) openChat();
  else closeChat();
});
byId("chat-back").addEventListener("click", () => {
  byId("chat-title").textContent = "Tin nhắn khách hàng";
  byId("chat-subtitle").textContent = `${chatCustomers.length} cuộc trò chuyện · Mô phỏng`;
  byId("chat-customer-list").hidden = false;
  byId("chat-conversation").hidden = true;
  byId("chat-back").hidden = true;
});
renderChatCustomers();
byId("chat-close").addEventListener("click", () => {
  closeChat();
  byId("chat-launcher").focus();
});

byId("chat-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const input = byId("chat-input");
  const text = input.value.trim();
  if (!text) return;
  const customerName = byId("chat-title").textContent;
  const customer = chatCustomers.find((item) => item.name === customerName);
  if (!customer) return;
  addChatMessage("operator", text);
  customer.messages.push({ sender: "operator", text });
  customer.preview = text;
  input.value = "";
});

refresh().catch((error) => showToast(error.message, true));
