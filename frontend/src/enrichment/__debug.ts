import { detectTechnologies } from "./extract";
import { bindTechnologies } from "./bind";
const { detected, conflicts } = detectTechnologies("Use React, PostgreSQL and Redis.");
console.log("DETECTED:", JSON.stringify(detected.map(d => ({ id: d.technologyId, cat: d.category, conf: d.confidence, hedged: d.hedged, mentions: d.mentions })), null, 1));
const nodes = [["ui-1","ui"],["service-1","service"],["database-1","database"],["cache-1","cache"]].map(([id,type])=>({id,type}));
const result = bindTechnologies(detected, nodes, {});
console.log("BINDS:", JSON.stringify(result.enrichedNodes.map(n => ({ id: n.nodeId, assignment: n.assignment && n.assignment.technologyId, candidates: n.candidates.map(c => c.technology.technologyId + ":" + c.confidence) })), null, 1));
console.log("UNPLACED:", result.unplaced.map(u => u.technologyId));
console.log("CONFLICTS:", JSON.stringify(result.conflicts));
