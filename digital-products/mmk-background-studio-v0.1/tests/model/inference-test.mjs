import * as ort from "onnxruntime-web";

console.log("=== MMK U2NETP INFERENCE TEST ===");

ort.env.wasm.numThreads = 1;

const session = await ort.InferenceSession.create(
  "models/u2netp/u2netp.onnx",
  {
    executionProviders: ["wasm"]
  }
);

const width = 320;
const height = 320;
const channels = 3;

// Simple synthetic RGB image.
const data = new Float32Array(width * height * channels);

for (let y = 0; y < height; y++) {
  for (let x = 0; x < width; x++) {
    const i = (y * width + x) * channels;

    // Bright square in the middle, darker background.
    const inside =
      x >= 80 && x < 240 &&
      y >= 80 && y < 240;

    const value = inside ? 1.0 : 0.05;

    data[i] = value;
    data[i + 1] = value;
    data[i + 2] = value;
  }
}

const inputTensor = new ort.Tensor(
  "float32",
  data,
  [1, 3, height, width]
);

const results = await session.run({
  "input.1": inputTensor
});

console.log("Inference: OK");

for (const name of session.outputNames) {
  const tensor = results[name];

  console.log(
    "Output:",
    name,
    "type:",
    tensor.type,
    "dims:",
    tensor.dims,
    "values:",
    tensor.data.length
  );
}

console.log("U2NETP INFERENCE TEST: PASS");
