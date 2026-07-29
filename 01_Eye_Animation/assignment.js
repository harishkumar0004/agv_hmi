(function () {
  "use strict";

  const TASK_LABELS = {
    food: "Food & Beverage",
    item: "Item / Amenity",
    housekeeping: "Housekeeping",
    other: "Other Task"
  };

  const task = { type: null, room: "", notes: "" };
  let step = "type";

  let stage, screen, panel, backBtn, title;
  let tiles, roomSelect, customField, customRoomInput, notesInput;
  let confirmBtn, doneBtn, confirmDetail, detailsSubtitle;

  function buildRoomOptions() {
    const floors = [1, 2, 3, 4, 5];
    const customOption = roomSelect.querySelector('option[value="__custom"]');

    floors.forEach((floor) => {
      const group = document.createElement("optgroup");
      group.label = `Floor ${floor}`;

      for (let n = 1; n <= 10; n += 1) {
        const num = floor * 100 + n;
        const opt = document.createElement("option");
        opt.value = String(num);
        opt.textContent = String(num);
        group.appendChild(opt);
      }

      roomSelect.insertBefore(group, customOption);
    });
  }

  function showStep(next) {
    step = next;

    panel.querySelectorAll(".ap-step").forEach((el) => {
      el.classList.toggle("is-active", el.dataset.step === next);
    });

    backBtn.style.visibility = next === "confirm" ? "hidden" : "visible";

    if (next === "type") title.textContent = "New Task";
    if (next === "details") title.textContent = TASK_LABELS[task.type] || "Task Details";
    if (next === "confirm") title.textContent = "Confirmed";
  }

  function validateDetails() {
    const room = roomSelect.value === "__custom" ? customRoomInput.value.trim() : roomSelect.value;
    confirmBtn.disabled = !room;
  }

  function openAssignment() {
    stage.dataset.mode = "assignment";
    panel.setAttribute("aria-hidden", "false");

    task.type = null;
    task.room = "";
    task.notes = "";
    roomSelect.value = "";
    customField.hidden = true;
    customRoomInput.value = "";
    notesInput.value = "";
    confirmBtn.disabled = true;

    showStep("type");
  }

  function closeAssignment() {
    stage.dataset.mode = "face";
    panel.setAttribute("aria-hidden", "true");
  }

  function bindEvents() {
    screen.addEventListener("click", () => {
      if (stage.dataset.mode === "assignment") {
        return;
      }
      openAssignment();
    });

    panel.addEventListener("click", (event) => event.stopPropagation());

    backBtn.addEventListener("click", () => {
      if (step === "details") {
        showStep("type");
        return;
      }
      closeAssignment();
    });

    tiles.forEach((tile) => {
      tile.addEventListener("click", () => {
        task.type = tile.dataset.taskType;
        detailsSubtitle.textContent = `${TASK_LABELS[task.type]} \u2014 enter details`;
        showStep("details");
      });
    });

    roomSelect.addEventListener("change", () => {
      customField.hidden = roomSelect.value !== "__custom";
      if (!customField.hidden) {
        customRoomInput.focus();
      }
      validateDetails();
    });

    customRoomInput.addEventListener("input", validateDetails);

    confirmBtn.addEventListener("click", () => {
      task.room = roomSelect.value === "__custom" ? customRoomInput.value.trim() : roomSelect.value;
      task.notes = notesInput.value.trim();

      confirmDetail.textContent = `Room ${task.room} \u00b7 ${TASK_LABELS[task.type]}${task.notes ? " \u00b7 " + task.notes : ""}`;
      showStep("confirm");

      window.dispatchEvent(new CustomEvent("robot-face:task-assigned", { detail: { ...task } }));

      if (window.RobotFace && typeof window.RobotFace.setEmotion === "function") {
        window.RobotFace.setEmotion("happy", { source: "task-assigned" });
      }
    });

    doneBtn.addEventListener("click", closeAssignment);
  }

  function init() {
    stage = document.getElementById("robotStage");
    screen = document.getElementById("screen");
    panel = document.getElementById("assignmentPanel");
    backBtn = document.getElementById("apBack");
    title = document.getElementById("apTitle");
    tiles = Array.from(document.querySelectorAll(".ap-tile"));
    roomSelect = document.getElementById("apRoomSelect");
    customField = document.getElementById("apCustomRoomField");
    customRoomInput = document.getElementById("apCustomRoom");
    notesInput = document.getElementById("apNotes");
    confirmBtn = document.getElementById("apConfirmBtn");
    doneBtn = document.getElementById("apDoneBtn");
    confirmDetail = document.getElementById("apConfirmDetail");
    detailsSubtitle = document.getElementById("apDetailsSubtitle");

    buildRoomOptions();
    bindEvents();

    window.RobotAssignment = {
      open: openAssignment,
      close: closeAssignment,
      get currentTask() {
        return { ...task };
      },
      get currentStep() {
        return step;
      }
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
}());
