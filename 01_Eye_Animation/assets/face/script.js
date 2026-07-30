let bridge = null;
(function () {
  "use strict";

  const stage = document.getElementById("robotStage");
  const screen = document.getElementById("screen");
  const faceSvg = document.getElementById("faceSvg");
  const buttons = Array.from(document.querySelectorAll("[data-emotion-button]"));
  const ears = Array.from(document.querySelectorAll(".ear"));

  const EMOTIONS = window.RobotEmotionDefinitions || {};
  console.log("RobotEmotionDefinitions:", window.RobotEmotionDefinitions);
  console.log("Available emotions:", Object.keys(EMOTIONS));
  const COMMAND_MAP = {
    NORMAL: "normal",
    HAPPY: "happy",
    ANGRY: "angry",
    SAD: "sad",
    EXCITED: "excited",
    SLEEPY: "sleepy"
  };
  const TRIGGER_TABLE = {
    singleTap: { emotion: "happy", condition: "Arduino reports one TTP223 tap", autoReturnMs: 5000 },
    doubleTap: { emotion: "excited", condition: "Arduino reports two quick TTP223 taps", autoReturnMs: 5000 },
    rapidHeadTaps: { emotion: "angry", condition: "4 taps within 2 seconds", autoReturnMs: 5000 },
    longTouch: { emotion: "sleepy", condition: "Arduino reports TTP223 touch held for more than 3 seconds", autoReturnMs: 5000 },
    batteryLowOrError: { emotion: "sad", condition: "low battery or robot error", autoReturnMs: 10000 }
  };

  const state = {
    currentEmotion: "normal",
    previousEmotion: null,
    emotionTimeout: 0,
    blinking: false,
    blinkTimer: 0,
    floatTime: 0,
    sparkleIndex: 0,
    veinIndex: 0,
    pointer: { x: 0, y: 0 },
    targetPointer: { x: 0, y: 0 },
    smoothedPointer: { x: 0, y: 0 }
  };

  function getConfig(emotion = state.currentEmotion) {
    return EMOTIONS[emotion] || EMOTIONS.normal;
  }

  function getFace(emotion = state.currentEmotion) {
    return document.querySelector(`[data-face="${emotion}"]`);
  }

  function getActiveParts() {
    const face = getFace();
    return {
      face,
      lids: face ? Array.from(face.querySelectorAll(".blink-lid")) : [],
      pupils: face ? Array.from(face.querySelectorAll(".pupil-group")) : [],
      whiskers: face ? Array.from(face.querySelectorAll(".whisker")) : [],
      sparkles: face ? Array.from(face.querySelectorAll(".svg-sparkle")) : [],
      veins: face ? Array.from(face.querySelectorAll(".anger-vein")) : [],
      tears: face ? Array.from(face.querySelectorAll(".tear")) : [],
      sadMouthLeft: face ? face.querySelector(".sad-mouth-left") : null,
      sadMouthRight: face ? face.querySelector(".sad-mouth-right") : null
    };
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function randomBetween(min, max) {
    return min + Math.random() * (max - min);
  }

  function updateDebugButtons() {
    buttons.forEach((button) => {
      button.classList.toggle("is-active", button.dataset.emotionButton === state.currentEmotion);
    });
  }

  function resetLids() {
    document.querySelectorAll(".blink-lid").forEach((lid) => {
      lid.setAttribute("height", "0");
    });
  }

  function resetPupils() {
    document.querySelectorAll(".pupil-group").forEach((pupil) => {
      pupil.setAttribute("transform", "");
    });
    state.targetPointer = { ...getConfig().pupilRest };
    state.smoothedPointer = { ...getConfig().pupilRest };
  }

  function clearEarOverrides() {
    ears.forEach((ear) => {
      ear.style.transition = "";
      ear.style.transform = "";
    });
  }

  function clearEmotionTimeout() {
    window.clearTimeout(state.emotionTimeout);
    state.emotionTimeout = 0;
  }

  function scheduleAutoReturn(config, options = {}) {
    clearEmotionTimeout();

    if (options.autoReturn === false || config.persistent || !config.autoReturnMs) {
      return;
    }

    state.emotionTimeout = window.setTimeout(() => {
      setEmotion("normal", { source: "auto-return", autoReturn: false });
    }, config.autoReturnMs);
  }

  function scheduleBlink() {
    window.clearTimeout(state.blinkTimer);
    const [minDelay, maxDelay] = getConfig().blinkDelay;
    state.blinkTimer = window.setTimeout(doBlink, randomBetween(minDelay, maxDelay));
  }

  function doBlink() {
    if (state.blinking) {
      return;
    }

    const config = getConfig();
    const { lids } = getActiveParts();

    if (!lids.length) {
      scheduleBlink();
      return;
    }

    state.blinking = true;
    let frame = 0;
    let direction = 1;

    function tick() {
      frame += direction;
      const height = Math.round((frame / config.blinkSteps) * config.blinkFullHeight);
      lids.forEach((lid) => lid.setAttribute("height", String(height)));

      if (direction === 1 && frame >= config.blinkSteps) {
        direction = -1;

        if (config.blinkHoldMs) {
          window.setTimeout(() => window.requestAnimationFrame(tick), config.blinkHoldMs);
          return;
        }
      }

      if (direction === -1 && frame <= 0) {
        lids.forEach((lid) => lid.setAttribute("height", "0"));
        state.blinking = false;
        scheduleBlink();
        return;
      }

      window.requestAnimationFrame(tick);
    }

    window.requestAnimationFrame(tick);
  }

  function updatePupilTarget(clientX, clientY) {
    const rect = screen.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const dx = clamp((clientX - centerX) / (rect.width / 2), -1, 1);
    const dy = clamp((clientY - centerY) / (rect.height / 2), -1, 1);
    const config = getConfig();

    state.pointer = { x: dx, y: dy };
    state.targetPointer = {
      x: dx * config.pupilRange.x + config.pupilRest.x,
      y: dy * config.pupilRange.y + config.pupilRest.y
    };
  }

  function renderPupils() {
    const config = getConfig();
    const { pupils } = getActiveParts();
    const smoothing = config.pupilSmoothing;

    if (smoothing >= 1) {
      state.smoothedPointer = { ...state.targetPointer };
    } else {
      state.smoothedPointer.x += (state.targetPointer.x - state.smoothedPointer.x) * smoothing;
      state.smoothedPointer.y += (state.targetPointer.y - state.smoothedPointer.y) * smoothing;
    }

    pupils.forEach((pupil) => {
      pupil.setAttribute("transform", `translate(${state.smoothedPointer.x},${state.smoothedPointer.y})`);
    });
  }

  function startAnimationLoop() {
    function loop() {
      const config = getConfig();
      const face = getFace();
      const parts = getActiveParts();

      state.floatTime += config.floatSpeed;
      renderPupils();

      if (face && state.currentEmotion === "normal") {
        face.style.transform = `translateY(${Math.sin(state.floatTime) * config.floatAmplitude}px)`;
      } else if (face) {
        face.style.transform = "";
      }

      if (state.currentEmotion === "sad" && parts.sadMouthLeft && parts.sadMouthRight) {
        const q = Math.sin(state.floatTime * 22) * 1.5;
        parts.sadMouthLeft.setAttribute("d", `M ${254 + q} ${328 + q * 0.3} Q 272 314 292 320`);
        parts.sadMouthRight.setAttribute("d", `M ${330 - q} ${328 + q * 0.3} Q 312 314 292 320`);
      }

      if (state.currentEmotion === "sad") {
        parts.tears.forEach((tear, index) => {
          const phase = (performance.now() / 24 + index * 90) % 180;
          const y = 258 + phase * 0.5;
          const opacity = Math.max(0, 0.75 - phase / 180);
          tear.setAttribute("cy", String(y));
          tear.setAttribute("opacity", String(opacity));
        });
      }

      window.requestAnimationFrame(loop);
    }

    window.requestAnimationFrame(loop);
  }

  function startWhiskerLoop() {
    function twitch() {
      const { whiskers } = getActiveParts();
      const baseOpacity = state.currentEmotion === "angry" ? "0.75" : state.currentEmotion === "excited" ? "0.75" : "0.7";

      whiskers.forEach((whisker) => {
        whisker.setAttribute("opacity", "1");
        window.setTimeout(() => whisker.setAttribute("opacity", baseOpacity), 180);
      });

      const delay = state.currentEmotion === "excited" ? randomBetween(500, 1100) : randomBetween(3500, 6500);
      window.setTimeout(twitch, delay);
    }

    window.setTimeout(twitch, 800);
  }

  function startHappySparkleLoop() {
    function popSparkle() {
      if (state.currentEmotion === "happy") {
        const { sparkles } = getActiveParts();
        const sparkle = sparkles[state.sparkleIndex % Math.max(sparkles.length, 1)];

        if (sparkle) {
          state.sparkleIndex += 1;
          sparkle.setAttribute("opacity", "1");
          sparkle.setAttribute("transform", "scale(1.4)");
          window.setTimeout(() => {
            sparkle.setAttribute("opacity", "0");
            sparkle.setAttribute("transform", "");
          }, 340);
        }
      }

      window.setTimeout(popSparkle, randomBetween(550, 950));
    }

    window.setTimeout(popSparkle, 800);
  }

  function startAngryVeinLoop() {
    function popVein() {
      if (state.currentEmotion === "angry") {
        const { veins } = getActiveParts();
        const vein = veins[state.veinIndex % Math.max(veins.length, 1)];

        if (vein) {
          state.veinIndex += 1;
          vein.setAttribute("opacity", "1");
          window.setTimeout(() => vein.setAttribute("opacity", "0"), 500);
        }
      }

      window.setTimeout(popVein, randomBetween(1600, 2800));
    }

    window.setTimeout(popVein, 1000);
  }

  function triggerHappyBurst() {
    const colors = ["#ffe066", "#ff69b4", "#66ffcc", "#ffb300", "#aaaaff"];

    for (let i = 0; i < 8; i += 1) {
      const dot = document.createElement("div");
      const angle = (i / 8) * Math.PI * 2;
      const distance = randomBetween(60, 100);

      dot.className = "burst-dot";
      dot.style.background = colors[i % colors.length];
      screen.appendChild(dot);

      window.requestAnimationFrame(() => {
        dot.style.transform = `translate(calc(-50% + ${Math.cos(angle) * distance}px), calc(-50% + ${Math.sin(angle) * distance}px))`;
        dot.style.opacity = "0";
      });

      window.setTimeout(() => dot.remove(), 620);
    }
  }

  function triggerEarFlinch() {
    ears.forEach((ear) => {
      ear.style.transition = "transform 0.12s ease";
      ear.style.transform = "rotate(-14deg) scaleX(0.88)";
      window.setTimeout(() => {
        ear.style.transform = "rotate(7deg)";
      }, 130);
      window.setTimeout(() => {
        ear.style.transform = "";
      }, 280);
    });
  }

  function triggerAngrySnap() {
    ears.forEach((ear) => {
      const isLeft = ear.classList.contains("ear-left");
      ear.style.transition = "transform 0.1s ease";
      ear.style.transform = isLeft ? "rotate(-35deg) scaleY(0.55)" : "rotate(35deg) scaleY(0.55)";
      window.setTimeout(() => {
        ear.style.transform = isLeft ? "rotate(-22deg) scaleY(0.7)" : "rotate(22deg) scaleY(0.7)";
      }, 180);
    });
  }

  function triggerInteractionBurst() {
    const action = getConfig().burst;

    if (action === "happyBurst") {
      triggerHappyBurst();
      return;
    }

    if (action === "angrySnap") {
      triggerAngrySnap();
      return;
    }

    triggerEarFlinch();
  }

  function normalizeEmotion(emotion) {
    return String(emotion || "").trim().toLowerCase();
  }

  function setEmotion(emotion, options = {}) {
    const nextEmotion = normalizeEmotion(emotion);
    const config = EMOTIONS[nextEmotion];

    if (!config) {
      console.warn(`Unknown emotion "${emotion}". Available emotions: ${Object.keys(EMOTIONS).join(", ")}`);
      return false;
    }

    state.previousEmotion = state.currentEmotion;
    state.currentEmotion = nextEmotion;
    stage.dataset.emotion = nextEmotion;
    faceSvg.dataset.activeEmotion = nextEmotion;

    clearEarOverrides();
    resetLids();
    resetPupils();
    updateDebugButtons();
    scheduleBlink();
    scheduleAutoReturn(config, options);

    window.dispatchEvent(new CustomEvent("robot-face:emotion-change", {
      detail: {
        currentEmotion: state.currentEmotion,
        previousEmotion: state.previousEmotion,
        source: options.source || "api"
      }
    }));

    return true;
  }

  function handleEmotionCommand(command) {
    const key = String(command || "").trim().toUpperCase();
    const emotion = COMMAND_MAP[key];

    if (!emotion) {
      console.warn(`Unknown emotion command "${command}".`);
      return false;
    }

    return setEmotion(emotion, { source: "backend-command" });
  }

  function connectSerialBridge() {
    if (!window.EventSource) {
      console.warn("EventSource is not available; serial bridge disabled.");
      return;
    }

    // The bridge serves this page too.  Use the page host so a browser on
    // another screen/device does not incorrectly connect to its own localhost.
    const bridgeOrigin = window.location.protocol === "file:"
      ? "http://127.0.0.1:8765"
      : `${window.location.protocol}//${window.location.host}`;
    const bridgeUrl = `${bridgeOrigin}/events`;
    const source = new EventSource(bridgeUrl);

    source.onmessage = (event) => {
      handleEmotionCommand(event.data);
    };

    source.onerror = () => {
      console.warn(`Serial bridge disconnected or unavailable at ${bridgeUrl}.`);
    };
  }

  function bindEvents() {
    document.addEventListener("mousemove", (event) => {
      updatePupilTarget(event.clientX, event.clientY);
    });

    document.addEventListener("mouseleave", resetPupils);
    //clicking in any in the screen trigger to the idle screen.
    screen.addEventListener("click", () => {

        triggerInteractionBurst();

        if (bridge) {
            bridge.onFaceTouched();
        }

    });

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        setEmotion(button.dataset.emotionButton, { source: "debug-panel" });
      });
    });

    window.addEventListener("message", (event) => {
      if (typeof event.data === "string") {
        handleEmotionCommand(event.data);
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.ctrlKey && event.key.toLowerCase() === "d") {
        event.preventDefault();
        stage.dataset.debug = stage.dataset.debug === "true" ? "false" : "true";
      }
    });
  }
  window.playEmotion = function (emotion) {
      console.log("Emotion requested:", emotion);

      setEmotion(emotion, {
          source: "python"
      });
  };
  function init() {
    if (new URLSearchParams(window.location.search).has("debug")) {
      stage.dataset.debug = "true";
    }

    window.setEmotion = setEmotion;
    window.handleEmotionCommand = handleEmotionCommand;
    window.RobotFace = {
      setEmotion,
      handleEmotionCommand,
      get currentEmotion() {
        return state.currentEmotion;
      },
      get previousEmotion() {
        return state.previousEmotion;
      },
      get emotionTimeout() {
        return state.emotionTimeout;
      },
      emotions: () => Object.keys(EMOTIONS),
      triggers: () => ({ ...TRIGGER_TABLE })
    };

    new QWebChannel(qt.webChannelTransport, function(channel) {
        bridge = channel.objects.bridge;
    });

    bindEvents();
    connectSerialBridge();
    updateDebugButtons();
    resetPupils();
    scheduleBlink();
    startAnimationLoop();
    startWhiskerLoop();
    startHappySparkleLoop();
    startAngryVeinLoop();
  }

  init();
}());
