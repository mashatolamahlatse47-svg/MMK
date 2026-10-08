import * as ort from "onnxruntime-web";

const modelPath = "models/u2netp/u2netp.onnx";

console.log("=== MMK U2NETP SESSION INSPECTION ===");

ort.env.wasm.numThreads = 1;

const session = await ort.InferenceSession.create(modelPath, {
  executionProviders: ["wasm"]
});

console.log("\nInput names:");
console.log(session.inputNames);

console.log("\nOutput names:");
console.log(session.outputNames);

console.log("\nSession keys:");
console.log(Object.keys(session));

console.log("\nSESSION INSPECTION: PASS");
