import * as ort from "onnxruntime-web";
import { statSync } from "node:fs";

const modelPath = "models/u2netp/u2netp.onnx";

console.log("=== MMK U2NETP MODEL LOAD TEST ===");
console.log("Model:", modelPath);
console.log("Model size:", statSync(modelPath).size, "bytes");

ort.env.wasm.numThreads = 1;

const session = await ort.InferenceSession.create(modelPath, {
  executionProviders: ["wasm"]
});

console.log("Model load: OK");
console.log("Inputs:", session.inputNames);
console.log("Outputs:", session.outputNames);
console.log("U2NETP TEST: PASS");
