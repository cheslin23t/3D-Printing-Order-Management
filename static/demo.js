(() => {
  let lastDialogTrigger = null;
  let toastTimer = null;

  const getDialog = (id) => document.getElementById(id);

  function openDialog(dialog, trigger) {
    if (!dialog) return;
    lastDialogTrigger = trigger || document.activeElement;
    if (typeof dialog.showModal === "function") dialog.showModal();
  }

  function closeDialog(dialog) {
    if (!dialog?.open) return;
    dialog.close();
  }

  function showToast(message) {
    const toast = document.querySelector("[data-toast]");
    if (!toast) return;
    window.clearTimeout(toastTimer);
    toast.textContent = message;
    toast.hidden = false;
    toastTimer = window.setTimeout(() => {
      toast.hidden = true;
    }, 4200);
  }

  function clearFieldError(field) {
    field.removeAttribute("aria-invalid");
    const errorId = field.dataset.error;
    if (!errorId) return;
    const error = document.getElementById(errorId);
    if (error) error.textContent = "";
  }

  function setFieldError(field, message) {
    field.setAttribute("aria-invalid", "true");
    const errorId = field.dataset.error;
    if (!errorId) return;
    const error = document.getElementById(errorId);
    if (error) error.textContent = message;
  }

  function validateOrderForm(form) {
    const required = [...form.querySelectorAll("[data-required='true']:not([disabled])")];
    let firstInvalid = null;
    required.forEach((field) => {
      clearFieldError(field);
      const value = field.value.trim();
      let message = "";
      if (!value) message = "Enter this information to continue.";
      if (value && field.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        message = "Enter a complete email address.";
      }
      if (value && field.name === "budget" && (!/^\d+$/.test(value) || Number(value) < 1)) {
        message = "Enter a budget of at least $1 using whole dollars.";
      }
      if (message) {
        setFieldError(field, message);
        if (!firstInvalid) firstInvalid = field;
      }
    });
    if (firstInvalid) {
      firstInvalid.focus();
      firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
      return false;
    }
    return true;
  }

  function syncModelFields(form) {
    const mode = form.elements.modelType?.value || "existing";
    const existing = form.querySelector("[data-model-fields='existing']");
    const custom = form.querySelector("[data-model-fields='custom']");
    if (!existing || !custom) return;
    existing.hidden = mode !== "existing";
    custom.hidden = mode !== "custom";
    existing.querySelectorAll("input, textarea, select").forEach((field) => {
      field.disabled = mode !== "existing";
      field.dataset.required = mode === "existing" ? "true" : "false";
      if (field.disabled) clearFieldError(field);
    });
    custom.querySelectorAll("input, textarea, select").forEach((field) => {
      field.disabled = mode !== "custom";
      if (field.name === "modelDetails") field.dataset.required = mode === "custom" ? "true" : "false";
      if (field.disabled) clearFieldError(field);
    });
  }

  function resetOrderDialog() {
    const form = document.querySelector("[data-order-form]");
    const confirmation = document.querySelector("[data-order-confirmation]");
    const formView = document.querySelector("[data-order-form-view]");
    if (!form || !confirmation || !formView) return;
    form.reset();
    form.querySelectorAll("[aria-invalid='true']").forEach(clearFieldError);
    confirmation.hidden = true;
    formView.hidden = false;
    syncModelFields(form);
  }

  document.addEventListener("click", (event) => {
    const openButton = event.target.closest("[data-dialog-open]");
    if (openButton) {
      openDialog(getDialog(openButton.dataset.dialogOpen), openButton);
      return;
    }

    const closeButton = event.target.closest("[data-dialog-close]");
    if (closeButton) {
      closeDialog(closeButton.closest("dialog"));
      return;
    }

    const resetButton = event.target.closest("[data-order-reset]");
    if (resetButton) {
      resetOrderDialog();
      document.querySelector("[data-order-form] input")?.focus();
      return;
    }

    const detailButton = event.target.closest("[data-detail-open]");
    if (detailButton) {
      const dialog = getDialog("record-dialog");
      if (!dialog) return;
      dialog.querySelector("[data-record-title]").textContent = detailButton.dataset.title || "Order details";
      const body = dialog.querySelector("[data-record-body]");
      body.replaceChildren();
      let details = {};
      try {
        details = JSON.parse(detailButton.dataset.details || "{}");
      } catch {
        details = { Details: "Sample record unavailable." };
      }
      Object.entries(details).forEach(([label, value]) => {
        const item = document.createElement("div");
        const term = document.createElement("dt");
        const description = document.createElement("dd");
        term.textContent = label;
        description.textContent = String(value);
        item.append(term, description);
        body.append(item);
      });
      dialog.dataset.rowId = detailButton.dataset.rowId || "";
      openDialog(dialog, detailButton);
      return;
    }

    const confirmButton = event.target.closest("[data-confirm-open]");
    if (confirmButton) {
      const dialog = getDialog("confirm-dialog");
      if (!dialog) return;
      dialog.dataset.action = confirmButton.dataset.action || "";
      dialog.dataset.rowId = confirmButton.dataset.rowId || "";
      dialog.querySelector("[data-confirm-title]").textContent = confirmButton.dataset.confirmTitle || "Confirm demo action";
      dialog.querySelector("[data-confirm-copy]").textContent = confirmButton.dataset.confirmCopy || "This changes only the current demo view.";
      const action = dialog.querySelector("[data-confirm-action]");
      action.textContent = confirmButton.dataset.confirmLabel || "Continue";
      action.className = `button ${confirmButton.dataset.intent || "primary"}`;
      openDialog(dialog, confirmButton);
      return;
    }

    const saveButton = event.target.closest("[data-save-row]");
    if (saveButton) {
      showToast("Demo changes saved in this browser view. Nothing was sent to a server.");
      return;
    }

    const confirmAction = event.target.closest("[data-confirm-action]");
    if (confirmAction) {
      const dialog = confirmAction.closest("dialog");
      const row = document.querySelector(`[data-row-id="${CSS.escape(dialog.dataset.rowId || "")}"]`);
      const action = dialog.dataset.action;
      if (row && ["approve", "deny", "archive"].includes(action)) row.remove();
      const empty = document.querySelector("[data-empty-row]");
      const remaining = document.querySelectorAll("tbody tr[data-row-id]").length;
      if (empty && remaining === 0) empty.hidden = false;
      closeDialog(dialog);
      const messages = {
        approve: "Submission approved in the demo. It would now become an active print.",
        deny: "Submission denied in the demo. No server data was changed.",
        archive: "Print archived in the demo. Refresh the page to restore it.",
      };
      showToast(messages[action] || "Demo action completed.");
    }
  });

  document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.addEventListener("close", () => {
      lastDialogTrigger?.focus?.();
      lastDialogTrigger = null;
    });
    dialog.addEventListener("click", (event) => {
      if (event.target !== dialog) return;
      const rect = dialog.getBoundingClientRect();
      const inside = event.clientX >= rect.left && event.clientX <= rect.right && event.clientY >= rect.top && event.clientY <= rect.bottom;
      if (!inside) closeDialog(dialog);
    });
  });

  const orderForm = document.querySelector("[data-order-form]");
  if (orderForm) {
    syncModelFields(orderForm);
    orderForm.elements.modelType?.addEventListener("change", () => syncModelFields(orderForm));
    orderForm.addEventListener("input", (event) => {
      if (event.target.matches("input, select, textarea")) clearFieldError(event.target);
    });
    orderForm.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!validateOrderForm(orderForm)) return;
      const values = new FormData(orderForm);
      const reference = `PR-${String(Math.floor(Math.random() * 900) + 100)}`;
      document.querySelector("[data-order-reference]").textContent = reference;
      document.querySelector("[data-order-name]").textContent = values.get("fullName");
      document.querySelector("[data-order-budget]").textContent = `$${values.get("budget")}`;
      document.querySelector("[data-order-form-view]").hidden = true;
      document.querySelector("[data-order-confirmation]").hidden = false;
      document.querySelector("[data-order-confirmation] h3")?.focus();
    });
  }
})();
