export { register, createAction } from "./registry.js";
export type { Action, ActionCtor } from "./base.js";

// Trigger registration side effects by importing each action module.
import "./jsonReplace.js";
import "./htmlReplace.js";
import "./regexReplace.js";
import "./fileReplace.js";
