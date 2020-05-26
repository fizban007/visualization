import { Engine } from "@babylonjs/core/Engines/engine";
import { Scene } from "@babylonjs/core/scene";
import { Vector3, Color3, Color4 } from "@babylonjs/core/Maths/math";
import { ArcRotateCamera } from "@babylonjs/core/Cameras/arcRotateCamera";
import { HemisphericLight } from "@babylonjs/core/Lights/hemisphericLight";
import { StandardMaterial } from "@babylonjs/core/Materials/standardMaterial";

import { SphereBuilder } from "@babylonjs/core/Meshes/Builders/sphereBuilder";
import { LinesBuilder } from "@babylonjs/core/Meshes/Builders/linesBuilder";
import { GlowLayer } from "@babylonjs/core/Layers/glowLayer";

// Load LoadingScreen for side effects
import "@babylonjs/core/Loading/loadingScreen";
import { AssetsManager, BinaryFileAssetTask } from "@babylonjs/core/Misc/assetsManager";
import { LinesMesh } from "@babylonjs/core/Meshes/linesMesh";

// import * as stats from "stats.js";
import Stats from "stats.js";
// import Stats = require("stats.js");

// Get the canvas element from the DOM.
const canvas = document.getElementById("renderCanvas") as HTMLCanvasElement;

// Associate a Babylon Engine to it.
const engine = new Engine(canvas);

// Create our first scene.
var scene = new Scene(engine);

scene.clearColor = new Color4(0, 0, 0, 1);

// This creates and positions a free camera (non-mesh)
var camera = new ArcRotateCamera("camera1", 0, 0, 10, new Vector3(0, 0, 0), scene);

// This targets the camera to scene origin
// camera.setTarget(Vector3.Zero());
camera.setPosition(new Vector3(20, 0, 0));

// This attaches the camera to the canvas
camera.attachControl(canvas, true);

// camera.allowUpsideDown = false;
camera.lowerRadiusLimit = 1;
camera.upperRadiusLimit = 100;
camera.wheelPrecision = 10.0;

// This creates a light, aiming 0,1,0 - to the sky (non-mesh)
var light = new HemisphericLight("light1", new Vector3(0, 1, 0), scene);

// Default intensity is 1. Let's dim the light a small amount
light.intensity = 0.7;

// Create a grid material
// var material = new GridMaterial("grid", scene);
var material = new StandardMaterial("mat", scene);
material.backFaceCulling = false;

// Our built-in 'sphere' shape. Params: name, subdivs, size, scene
// var sphere = Mesh.CreateSphere("sphere1", 16, 2, scene);
var star = SphereBuilder.CreateSphere("star",
    { diameter: 2 }, scene);

// Affect a material
star.material = material;

// Create an asset manager and load field line
var assetsManager = new AssetsManager(scene);
assetsManager.useDefaultLoadingScreen = true;

for (var i = 0; i < 6; i++) {
    assetsManager.addBinaryFileTask("loadLine" + i, "data/line_" + i + "_000000");
}

var lines : LinesMesh[] = [];

assetsManager.load();
assetsManager.onFinish = function(tasks) {
    tasks.forEach( (element) => {
        // console.log(task.data);
        var task = element as BinaryFileAssetTask;
        var floatView = new Float32Array(task!.data);
        var vertices: Vector3[] = [];
        var colors: Color4[] = [];
        for (var i = 0; i < floatView.length / 3; i++) {
            vertices.push(new Vector3(floatView[i * 3 + 1],
                                      floatView[i * 3 + 2],
                                      floatView[i * 3]));
            colors.push(new Color4(0, 1, 0, 1));
        }
        lines.push(LinesBuilder.CreateLines("fieldline0", {
            points: vertices,
            useVertexAlpha: false,
            colors: colors,
        }, scene));

    });
}
var gl = new GlowLayer("glow", scene);
gl.intensity = 1.5;
gl.customEmissiveColorSelector = (mesh, subMesh, material, result) => {
    lines.forEach( (line) => {
        if (mesh == line) {
            result.set(0, 1, 0, 0.5);
        }
    } );
    if (mesh == star) {
        result.set(0, 0, 0, 1);
    }
}

var st = new Stats();
st.showPanel(0); // 0: fps, 1: ms, 2: mb, 3+: custom
document.body.appendChild(st.dom);

// Render every frame
engine.runRenderLoop(() => {
    st.begin();
    scene.render();
    st.end();
});
