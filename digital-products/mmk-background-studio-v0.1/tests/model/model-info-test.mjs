import * as ort from "onnxruntime-web";

const modelPath = "models/u2netp/u2netp.onnx";

console.log("=== MMK U2NETP MODEL INFO ===");

ort.env.wasm.numThreads = 1;

const session = await ort.InferenceSession.create(modelPath, {
  executionProviders: ["wasm"]
});

const input = session.inputMetadata["input.1"];

console.log("Input metadata:");
console.log(input);

console.log("\nOutput metadata:");

for (const name of session.outputNames) {
  console.log(name, session.outputMetadata[name]);
}

console.log("\nMODEL INFO TEST: PASS");
