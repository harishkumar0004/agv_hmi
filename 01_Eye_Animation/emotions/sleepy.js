window.RobotEmotionDefinitions = window.RobotEmotionDefinitions || {};
window.RobotEmotionDefinitions.sleepy = {
  name: "sleepy",
  autoReturnMs: 5000,
  blinkDelay: [3500, 6000],
  blinkSteps: 18,
  blinkFullHeight: 236,
  blinkHoldMs: 400,
  floatSpeed: 0.008,
  floatAmplitude: 5,
  pupilRange: { x: 8, y: 6 },
  pupilSmoothing: 0.03,
  pupilRest: { x: 0, y: 0 },
  burst: "earFlinch"
};
