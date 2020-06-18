import { Scene } from "@babylonjs/core/scene";
import { Nullable } from "@babylonjs/core/types";
import { LinesMesh } from "@babylonjs/core/Meshes/linesMesh";
import { LinesBuilder } from "@babylonjs/core/Meshes/Builders/linesBuilder";

export declare class FieldlineBuilder {

    static CreateFieldlines(name: string, options: {

    }, scene: Nullable<Scene>): LinesMesh;

}
