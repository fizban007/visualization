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

import Stats from "stats.js";
import { int } from "@babylonjs/core/types";
import { KeyboardEventTypes } from "@babylonjs/core/Events/keyboardEvents";
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

var lines: LinesMesh[][] = [];
var line_meshes: LinesMesh;
var buffers: Vector3[][][] = [];

var n_init: int = 100;
var n_max: int = 400;
var n_current: int = n_init;
var n_prev: int = n_current;
var is_playing: boolean = false;

for (var n = 0; n <= n_max - n_init; n++) {
    // lines.push([]);
    buffers.push([]);
}

function create_line_buffer(j: int, n: int, lines: LinesMesh[][]) {
    return function(task: BinaryFileAssetTask) {
        var floatView = new Float32Array(task.data);
        var vertices: Vector3[] = [];
        for (var i = 0; i < floatView.length / 3; i++) {
            vertices.push(new Vector3(floatView[i * 3 + 1],
                floatView[i * 3 + 2],
                floatView[i * 3]));
        }
        buffers[j - n_init].push(vertices);
    }
}

function update_lines(n: int) {
    scene.removeMesh(line_meshes);
    line_meshes = LinesBuilder.CreateLineSystem("fieldlines", {
        lines: buffers[n - n_init],
        useVertexAlpha: false,
    }, scene);
}

function create_lines(j: int, n: int, lines: LinesMesh[][]) {
    return function(task: BinaryFileAssetTask) {
        var floatView = new Float32Array(task.data);
        var vertices: Vector3[] = [];
        var colors: Color4[] = [];
        for (var i = 0; i < floatView.length / 3; i++) {
            vertices.push(new Vector3(floatView[i * 3 + 1],
                floatView[i * 3 + 2],
                floatView[i * 3]));
            colors.push(new Color4(0, 1, 0, 1));
        }
        // console.log(n, j, "loading finished");
        var l = LinesBuilder.CreateLines("fieldline_" + j + "_" + n, {
            points: vertices,
            useVertexAlpha: false,
            colors: colors,
        }, scene);
        if (j != n_init) {
            l.setEnabled(false);
        }
        lines[j - n_init].push(l);
    }
}

function enable_lines(n: int, n_prev: int) {
    lines[n_prev - n_init].forEach((line) => {
        line.setEnabled(false);
    });
    lines[n - n_init].forEach((line) => {
        line.setEnabled(true);
    });
}

var linetask = assetsManager.addTextFileTask("lines", "fieldlines/10.0/200");
linetask.onSuccess = function(task) {
    // console.log(task.text);
	var response = JSON.parse(task.text);
    // console.log("response is", response);
    for (var i = 0; i < response.length; i++) {
        buffers[0].push(response[i].map((v: Array<number>) => new Vector3(v[0], v[1], v[2])));
    }
    console.log(buffers[0]);
    line_meshes = LinesBuilder.CreateLineSystem("fieldlines", {
        lines: buffers[0],
        useVertexAlpha: false,
    }, scene);
    // line_meshes = LinesBuilder.CreateLines("fieldlines", {
    //     points: buffers[0][0],
    // }, scene);
    line_meshes.color = new Color3(0, 1, 0);

    // line_meshes.enableEdgesRendering();
	// line_meshes.edgesWidth = 20.0;
	// line_meshes.edgesColor = new Color4(0, 1, 0, 1);
}
// for (var n = 0; n < 6; n++) {
//     for (var j = n_init; j <= n_max; j++) {
//         var linetask = assetsManager.addBinaryFileTask("loadLine" + n + "_" + (j * 500),
//             "data/line_" + n + "_" + ("000000" + j * 500).slice(-6));
//         // linetask.onSuccess = create_lines(j, n, lines);
//         linetask.onSuccess = create_line_buffer(j, n, lines);
//     }
// }
// function create_load_task(n: int, num_line: int) {
//     var linetask = assetsManager.addBinaryFileTask("loadLine" + num_line + "_" + (n * 500),
//         "data/line_" + num_line + "_" + ("000000" + n * 500).slice(-6));
//     linetask.onSuccess = function() {
//         console.log("Finished loading ", n, num_line);
//         create_lines(n, num_line, lines);
//         if (n < n_max) {
//             create_load_task(n + 1, num_line);
//         }
//     }
// }

// for (var n = 0; n < 6; n++) {
//     create_load_task(n_init, n);
// }

function show_next_frame() {
    n_prev = n_current;
    n_current += 1;
    if (n_current > n_max) n_current = n_init;
    // enable_lines(n_current, n_prev);
    update_lines(n_current);
}

function show_prev_frame() {
    n_prev = n_current;
    n_current -= 1;
    if (n_current < n_init) n_current = n_max;
    // enable_lines(n_current, n_prev);
    update_lines(n_current);
}

assetsManager.onFinish = function(tasks) {
    // update_lines(n_init);
    var gl = new GlowLayer("glow", scene);
    gl.intensity = 0.5;
    gl.customEmissiveColorSelector = (mesh, subMesh, material, result) => {
        if (mesh == line_meshes)
            result.set(0, 1, 0, 0.5);
        if (mesh == star)
            result.set(0, 0, 0, 1);
    }

    var st = new Stats();
    st.showPanel(0); // 0: fps, 1: ms, 2: mb, 3+: custom
    document.body.appendChild(st.dom);

    // Add keypress events
    // scene.onKeyboardObservable.add((kbInfo) => {
    //     if (kbInfo.type == KeyboardEventTypes.KEYUP) {
    //         if (kbInfo.event.key == "ArrowRight") {
    //             show_next_frame();
    //         } else if (kbInfo.event.key == "ArrowLeft") {
    //             show_prev_frame();
    //         } else if (kbInfo.event.key == " ") {
    //             is_playing = !is_playing;
    //         }
    //     }
    // });

    // Render every frame
    var startTime = Date.now();

    engine.runRenderLoop(() => {
        st.begin();
        if (is_playing) {
            var currentTime = Date.now();
            var timeDiff = currentTime - startTime;
            if (timeDiff > 40) {
                // show_next_frame();
                startTime = currentTime;
            }
        }
        scene.render();
        st.end();
    });
}
// console.log(assetsManager.)
assetsManager.loadAsync();
