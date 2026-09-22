// Presentation settings never change the collision or scoring simulation.
export function qualityProfile({coarse=false,width=1280,dpr=1,webgl2=true}={}){
 const mobile=coarse||width<700;
 return {name:mobile?'mobile':'desktop',pixelRatio:Math.min(2,Math.max(1,dpr)),shadowSize:mobile?1024:2048,samples:webgl2?(mobile?2:4):1,ssao:webgl2&&!mobile,bloom:!mobile,anisotropy:mobile?4:8};
}
export function createMotion(){return{lean:0,pitch:0,compression:0,velocity:0,wheelAngle:0};}
export function landingImpulse(motion){motion.velocity=-1.6;}
export function advanceMotion(motion,{dt,laneDelta=0,airborne=false,speed=0,active=true}){
 const t=Math.min(dt,1/20);if(!active)return motion;
 const target=airborne?0:Math.max(-.52,Math.min(.52,-laneDelta*.25));
 motion.lean+=(target-motion.lean)*(1-Math.exp(-16*t));
 // Critically damped suspension with a small overshoot on touchdown.
 const acceleration=-180*motion.compression-19*motion.velocity;
 motion.velocity+=acceleration*t;motion.compression+=motion.velocity*t;
 motion.compression=Math.max(-.12,Math.min(.045,motion.compression));
 motion.wheelAngle=(motion.wheelAngle-speed*t/.39)%(Math.PI*2);
 return motion;
}
