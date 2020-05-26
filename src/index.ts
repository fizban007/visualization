import { Engine } from "@babylonjs/core/Engines/engine";
import { Scene } from "@babylonjs/core/scene";
import { Vector3 } from "@babylonjs/core/Maths/math";
import { ArcRotateCamera } from "@babylonjs/core/Cameras/arcRotateCamera";
import { HemisphericLight } from "@babylonjs/core/Lights/hemisphericLight";
import { Mesh } from "@babylonjs/core/Meshes/mesh";
import { GridMaterial } from "@babylonjs/materials/grid";
import { StandardMaterial } from "@babylonjs/core/Materials/standardMaterial";

import { SphereBuilder } from "@babylonjs/core/Meshes/Builders/sphereBuilder";
// Required side effects to populate the Create methods on the mesh class.
// Without this, the bundle would be smaller but the createXXX methods from mesh
// would not be accessible.
import "@babylonjs/core/Meshes/meshBuilder";

// Get the canvas element from the DOM.
const canvas = document.getElementById("renderCanvas") as HTMLCanvasElement;

// Associate a Babylon Engine to it.
const engine = new Engine(canvas);

// Create our first scene.
var scene = new Scene(engine);

// This creates and positions a free camera (non-mesh)
var camera = new ArcRotateCamera("camera1", 0, 0, 10, new Vector3(0, 0, 0), scene);

// This targets the camera to scene origin
// camera.setTarget(Vector3.Zero());
camera.setPosition(new Vector3(0, 5, 10));

// This attaches the camera to the canvas
camera.attachControl(canvas, true);

// camera.allowUpsideDown = false;
camera.lowerRadiusLimit = 1;
camera.upperRadiusLimit = 100;

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
var sphere = SphereBuilder.CreateSphere("sphere1",
                                        {diameter: 2}, scene);

// Affect a material
sphere.material = material;

// Render every frame
engine.runRenderLoop(() => {
    scene.render();
});
