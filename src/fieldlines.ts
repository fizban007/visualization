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
camera.upperRadiusLimit = 200;
camera.wheelPrecision = 10.0;
camera.inputs.remove(camera.inputs.attached.keyboard);

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

var is_loaded: boolean[] = [];
var lines: LinesMesh[] = [];
var buffers: Vector3[][][] = [];

var data_path = document.getElementById("dataPath")!.innerText;
console.log("path is", data_path);
var load_data_task = assetsManager.addTextFileTask("data", "/load_cart/\"" + data_path + "\"");
load_data_task.onSuccess = function(task) {
    var response = JSON.parse(task.text);
    console.log("steps are", response);

    var n_init: int = response[0];
    var n_max: int = response[response.length - 1];
    var n_current: int = n_init;
    var n_prev: int = n_current;
    var is_playing: boolean = false;

    for (var n = 0; n <= n_max - n_init; n++) {
        is_loaded.push(false);
        lines.push(LinesBuilder.CreateLineSystem("fieldlines" + n, {
            lines: [],
        }, scene));
        buffers.push([]);
    }

    function enable_lines(n: int, n_prev: int) {
        if (is_loaded[n_prev - n_init]) {
            lines[n_prev - n_init].setEnabled(false);
        }
        if (is_loaded[n - n_init]) {
            lines[n - n_init].setEnabled(true);
        } else {
            load_line_data(n);
        }
    }

    function load_line_data(n: int) {
        if (buffers[n - n_init].length === 0) {
            // var linetask = assetsManager.addTextFileTask("lines", "fieldlines/10.0/200");
            // linetask.onSuccess = function(task) {
            console.log("loading", "fieldlines/" + n + "/10.0/100");
            fetch("/fieldlines/" + n + "/10.0/200")
                .then(response => response.json())
                .then(data => {
                    // console.log(task.text);
	                // var response = JSON.parse(task.text);
                    console.log("response is", response);
                    for (var i = 0; i < data.length; i++) {
                        buffers[n - n_init].push(data[i].map((v: Array<number>) => new Vector3(v[1], v[2], v[0])));
                    }
                    lines[n - n_init] = LinesBuilder.CreateLineSystem("fieldlines" + n, {
                        lines: buffers[n - n_init],
                        useVertexAlpha: false,
                    }, scene);
                    lines[n - n_init].color = new Color3(0, 1, 0);
                    lines[n - n_init].setEnabled(n === n_current);
                    is_loaded[n - n_init] = true;
                });
        }
    }

    load_line_data(n_init);

    function show_next_frame() {
        n_prev = n_current;
        n_current += 1;
        if (n_current > n_max) n_current = n_init;
        enable_lines(n_current, n_prev);
        // update_lines(n_current);
    }

    function show_prev_frame() {
        n_prev = n_current;
        n_current -= 1;
        if (n_current < n_init) n_current = n_max;
        enable_lines(n_current, n_prev);
        // update_lines(n_current);
    }

    // assetsManager.onFinish = function(tasks) {
        // update_lines(n_init);
    var gl = new GlowLayer("glow", scene);
    gl.intensity = 0.5;
    gl.customEmissiveColorSelector = (mesh, subMesh, material, result) => {
        if (mesh == star)
            result.set(0, 0, 0, 1);
        else
            result.set(0, 1, 0, 0.5);
    }

    var st = new Stats();
    st.showPanel(0); // 0: fps, 1: ms, 2: mb, 3+: custom
    document.body.appendChild(st.dom);

    // Add keypress events
    scene.onKeyboardObservable.add((kbInfo) => {
        if (kbInfo.type == KeyboardEventTypes.KEYUP) {
            if (kbInfo.event.key == "ArrowRight") {
                show_next_frame();
            } else if (kbInfo.event.key == "ArrowLeft") {
                show_prev_frame();
            } else if (kbInfo.event.key == " ") {
                is_playing = !is_playing;
            }
        }
    });

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
    // }
    // console.log(assetsManager.)
}

assetsManager.loadAsync();
