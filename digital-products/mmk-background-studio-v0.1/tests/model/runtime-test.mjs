import * as ort from "onnxruntime-web";

console.log("=== MMK ONNX RUNTIME TEST ===");
console.log("ONNX Runtime version:", ort.env.version);
console.log("WASM available:", !!ort.env.wasm);
console.log("Runtime import: OK");
