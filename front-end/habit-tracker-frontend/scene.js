import * as THREE from 'three';
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer.js';
import * as CANNON from 'cannon-es';

let scene, camera, renderer, labelRenderer, world;
let characterGroup;
// Body parts
let head, neck, torso, leftUpperArm, rightUpperArm, leftForearm, rightForearm;
let leftThigh, rightThigh, leftShin, rightShin, leftFoot, rightFoot;

let steps = [], pointLights = [], particles;
let clock = new THREE.Clock();

// States & Timing
let currentStepIdx = 0;
let phase = 'idle'; // reach, plant, push, recover, triumph
let phaseTimer = 0;
let isPlaying = false;

const stepNames = ["Wake Up", "Hydrate", "Exercise", "Read", "Reflect", "Plan", "Grow"];

// Physics bodies
let footBody;

const PHYSICS = {
  STEP_HALF_EXTENTS: new CANNON.Vec3(1.5, 0.25, 0.75) // width 3, height 0.5, depth 1.5
};

export const initScene = (containerId) => {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  container.innerHTML = '';

  // 1. Scene
  scene = new THREE.Scene();
  scene.add(new THREE.AmbientLight(0xffffff, 0.05)); // Very dim

  // 2. Camera
  camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
  camera.position.set(-8, 6, 12);
  camera.lookAt(0, 2, 0);

  // 3. Renderers
  renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  container.appendChild(renderer.domElement);

  labelRenderer = new CSS2DRenderer();
  labelRenderer.setSize(container.clientWidth, container.clientHeight);
  labelRenderer.domElement.style.position = 'absolute';
  labelRenderer.domElement.style.top = '0px';
  labelRenderer.domElement.style.pointerEvents = 'none';
  container.appendChild(labelRenderer.domElement);

  // 4. Physics World (Part 5)
  world = new CANNON.World({
    gravity: new CANNON.Vec3(0, -9.8, 0),
  });

  // 5. Build Scene
  createStairs();
  createCharacter(); // Part 1
  createParticles();

  window.addEventListener('resize', onWindowResize);
  
  isPlaying = true;
  clock.start();
  
  // Start sequence
  currentStepIdx = 0;
  startPhase('reach');
  
  animate();
};

export const disposeScene = () => {
  isPlaying = false;
  window.removeEventListener('resize', onWindowResize);
  if (renderer) {
    renderer.dispose();
    renderer.domElement.remove();
  }
  if (labelRenderer) {
    labelRenderer.domElement.remove();
  }
};

const createStairs = () => {
  steps = [];
  pointLights = [];
  
  const stepMaterial = new THREE.MeshStandardMaterial({ 
    color: 0x111111, roughness: 0.8, metalness: 0.2 
  });
  const edgeMaterial = new THREE.LineBasicMaterial({ color: 0x4f9eff, transparent: true, opacity: 0.3 });

  for (let i = 0; i < 7; i++) {
    const width = 3;
    const height = 0.5;
    const depth = 1.5;
    
    const px = i * 1.5 - 4.5;
    const py = i * 0.75;
    const pz = -i * 0.5; 

    // Visual Mesh
    const geometry = new THREE.BoxGeometry(width, height, depth);
    const mesh = new THREE.Mesh(geometry, stepMaterial);
    mesh.position.set(px, py, pz);
    scene.add(mesh);
    
    // Glowing edges
    const edges = new THREE.EdgesGeometry(geometry);
    const line = new THREE.LineSegments(edges, edgeMaterial);
    line.position.copy(mesh.position);
    scene.add(line);

    // Physics Body (Part 5)
    const stepShape = new CANNON.Box(PHYSICS.STEP_HALF_EXTENTS);
    const stepBody = new CANNON.Body({ mass: 0 }); // static
    stepBody.addShape(stepShape);
    stepBody.position.set(px, py, pz);
    world.addBody(stepBody);

    // CSS Label (Part 4) - Top front-left vertex
    const labelDiv = document.createElement('div');
    labelDiv.className = 'step-label';
    labelDiv.textContent = stepNames[i];
    labelDiv.style.fontFamily = 'Inter';
    labelDiv.style.fontSize = '10px';
    labelDiv.style.textTransform = 'uppercase';
    labelDiv.style.letterSpacing = '2px';
    labelDiv.style.color = '#4F9EFF';
    labelDiv.style.opacity = '0.6';
    
    const label = new CSS2DObject(labelDiv);
    // Offset to front left edge (x: -width/2, y: height/2, z: depth/2)
    label.position.set(-width/2 + 0.2, height/2 + 0.5, depth/2 - 0.2);
    mesh.add(label);

    steps.push({ 
      mesh, 
      body: stepBody, 
      topY: py + height/2, // Part 2: Exact top Y coordinate
      x: px, 
      z: pz,
      baseScaleY: 1.0
    });

    // Trail Light (Part 10)
    const pLight = new THREE.PointLight(0x4f9eff, 0, 4); 
    pLight.position.set(px, py - 0.5, pz); // underneath
    scene.add(pLight);
    pointLights.push({ light: pLight, timer: 0 });
  }
};

const createCharacter = () => {
  // Part 1
  characterGroup = new THREE.Group();
  
  // Flat material for pure silhouette
  const mat = new THREE.MeshBasicMaterial({ color: 0xF0EDE6 });

  // Helpers to create pivot groups easily so rotations work from joints (shoulders, knees, hips)
  const createLimb = (geometry, yOffset) => {
    const mesh = new THREE.Mesh(geometry, mat);
    mesh.position.y = yOffset;
    const group = new THREE.Group();
    group.add(mesh);
    return { mesh, group };
  };

  // Torso
  torso = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.4, 0.15), mat);
  torso.position.y = 0.6; // Hip height
  characterGroup.add(torso);

  // Neck
  neck = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.1), mat);
  neck.position.y = 0.25;
  torso.add(neck);

  // Head
  head = new THREE.Mesh(new THREE.SphereGeometry(0.15), mat);
  head.position.y = 0.1;
  neck.add(head);

  // Left Arm (Shoulder joint)
  const lua = createLimb(new THREE.CylinderGeometry(0.06, 0.06, 0.25), -0.125);
  leftUpperArm = lua.group;
  leftUpperArm.position.set(-0.2, 0.15, 0); // left shoulder
  leftUpperArm.rotation.z = 30 * Math.PI / 180; // 30 deg outward
  torso.add(leftUpperArm);

  const lfa = createLimb(new THREE.CylinderGeometry(0.05, 0.05, 0.2), -0.1);
  leftForearm = lfa.group;
  leftForearm.position.y = -0.25; // Elbow
  leftForearm.rotation.z = -10 * Math.PI / 180;
  leftUpperArm.add(leftForearm);

  // Right Arm
  const rua = createLimb(new THREE.CylinderGeometry(0.06, 0.06, 0.25), -0.125);
  rightUpperArm = rua.group;
  rightUpperArm.position.set(0.2, 0.15, 0);
  rightUpperArm.rotation.z = -30 * Math.PI / 180;
  rightUpperArm.rotation.x = -Math.PI / 4; // rotated backward
  torso.add(rightUpperArm);

  const rfa = createLimb(new THREE.CylinderGeometry(0.05, 0.05, 0.2), -0.1);
  rightForearm = rfa.group;
  rightForearm.position.y = -0.25;
  rightForearm.rotation.z = 10 * Math.PI / 180;
  rightUpperArm.add(rightForearm);

  // Left Leg (Hip joint)
  const lt = createLimb(new THREE.CylinderGeometry(0.08, 0.08, 0.28), -0.14);
  leftThigh = lt.group;
  leftThigh.position.set(-0.1, -0.2, 0);
  torso.add(leftThigh);

  const ls = createLimb(new THREE.CylinderGeometry(0.06, 0.06, 0.25), -0.125);
  leftShin = ls.group;
  leftShin.position.y = -0.28; // Knee
  leftThigh.add(leftShin);
  
  leftFoot = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.06, 0.2), mat);
  leftFoot.position.set(0, -0.25, 0.05);
  leftShin.add(leftFoot);

  // Right Leg
  const rt = createLimb(new THREE.CylinderGeometry(0.08, 0.08, 0.28), -0.14);
  rightThigh = rt.group;
  rightThigh.position.set(0.1, -0.2, 0);
  rightThigh.rotation.x = Math.PI / 4; // Raised mid-step
  torso.add(rightThigh);

  const rs = createLimb(new THREE.CylinderGeometry(0.06, 0.06, 0.25), -0.125);
  rightShin = rs.group;
  rightShin.position.y = -0.28;
  rightThigh.add(rightShin);

  rightFoot = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.06, 0.2), mat);
  rightFoot.position.set(0, -0.25, 0.05);
  rightShin.add(rightFoot);

  // Physics Foot (represents body weight collision)
  footBody = new CANNON.Body({
    mass: 1, // Dynamic
    shape: new CANNON.Box(new CANNON.Vec3(0.1, 0.1, 0.1)),
    fixedRotation: true
  });
  world.addBody(footBody);

  scene.add(characterGroup);
  
  // Start config
  resetCharacterToStep(0);
};

const resetCharacterToStep = (idx) => {
  currentStepIdx = idx;
  const s = steps[idx];
  // Part 2
  const exactY = s.topY + 0.05; // Base offset to feet
  
  // Position slightly behind the edge 
  characterGroup.position.set(s.x - 1.2, exactY, s.z + 0.3);
  characterGroup.rotation.y = Math.PI / 6; // Angled slightly
  
  footBody.position.set(s.x - 1.2, exactY, s.z + 0.3);
  footBody.velocity.set(0,0,0);
  
  // Default pose
  torso.rotation.set(0,0,0);
  leftThigh.rotation.set(0,0,0);
  rightThigh.rotation.set(Math.PI/4,0,0); // mid-step rest
  leftShin.rotation.set(0,0,0);
  rightShin.rotation.set(-0.2,0,0);
  leftUpperArm.rotation.x = 0;
  rightUpperArm.rotation.x = -Math.PI/4;
};

const createParticles = () => {
  const particleGeo = new THREE.BufferGeometry();
  const particleCount = 60;
  const posArray = new Float32Array(particleCount * 3);
  const velArray = [];
  
  for(let i = 0; i < particleCount; i++) {
    posArray[i*3] = 0;
    posArray[i*3+1] = 0;
    posArray[i*3+2] = 0;
    velArray.push((Math.random() - 0.5) * 3, Math.random() * 4, (Math.random() - 0.5) * 3);
  }
  
  particleGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
  const particleMat = new THREE.PointsMaterial({
    size: 0.06, color: 0xFFD700, transparent: true, opacity: 0, blending: THREE.AdditiveBlending
  });
  
  particles = new THREE.Points(particleGeo, particleMat);
  particles.userData = { velocities: velArray, active: false, age: 0 };
  
  const topStep = steps[6];
  particles.position.set(topStep.x - 0.5, topStep.topY + 1, topStep.z + 0.5);
  scene.add(particles);
};

const triggerParticles = () => {
  particles.userData.active = true;
  particles.userData.age = 0;
  particles.material.opacity = 1;
};

// -- STATE MACHINE -- 
const startPhase = (newPhase) => {
  phase = newPhase;
  phaseTimer = 0;
  
  if (phase === 'plant') {
    // Impact physics impulse (Part 6)
    footBody.velocity.y = -2; // Send physics body down
    // Trail Light (Part 10)
    pointLights[currentStepIdx].light.intensity = 4.0;
    pointLights[currentStepIdx].timer = 1.0;
  }
};

const processStateMachine = (dt) => {
  phaseTimer += dt;
  const t = clock.elapsedTime * 6; // Walk speed
  
  // Micro-wobble (Part 8)
  torso.rotation.z += (Math.random() - 0.5) * 0.01;
  
  const currentStep = steps[Math.max(0, currentStepIdx - 1)];
  const nextStep = steps[currentStepIdx];
  
  // Kinematic walk cycle baseline (Part 3)
  const updateWalkCycle = () => {
    rightThigh.rotation.x = Math.sin(t) * 0.4;
    leftThigh.rotation.x = Math.sin(t + Math.PI) * 0.4;
    rightUpperArm.rotation.x = Math.sin(t + Math.PI) * 0.3;
    leftUpperArm.rotation.x = Math.sin(t) * 0.3;
  };
  
  if (phase === 'reach') {
    // 0.6 seconds duration
    updateWalkCycle();
    
    // Front leg kicks up (Part 6)
    const prog = Math.min(1, phaseTimer / 0.6);
    rightThigh.rotation.x = THREE.MathUtils.lerp(0, 55 * Math.PI/180, prog);
    rightShin.rotation.x = THREE.MathUtils.lerp(0, -40 * Math.PI/180, prog);
    
    // Lean backward hesitating
    torso.rotation.x = THREE.MathUtils.lerp(0, -8 * Math.PI/180, prog);
    
    // Position moving towards next step
    const startX = currentStep.x - 1.2;
    const startZ = currentStep.z + 0.3;
    const targetX = nextStep.x - 1.2;
    const targetZ = nextStep.z + 0.3;
    
    characterGroup.position.x = THREE.MathUtils.lerp(startX, targetX, prog);
    characterGroup.position.z = THREE.MathUtils.lerp(startZ, targetZ, prog);
    
    // Slip slightly back (Part 5)
    if (prog > 0.3 && prog < 0.6) {
      characterGroup.position.x -= 0.04 * (1 - prog); // subtle slide back
    }
    
    if (phaseTimer >= 0.6) startPhase('plant');
    
  } else if (phase === 'plant') {
    // 0.15 seconds duration
    const prog = Math.min(1, phaseTimer / 0.15);
    
    // Step vibration absorbs impact
    nextStep.mesh.scale.y = 1.0 - (Math.sin(prog * Math.PI) * 0.02); // 1.0 to 0.98 to 1.0
    
    // Link character Y strictly to physics body for the bounce (Part 5)
    characterGroup.position.y = footBody.position.y;
    
    // Part 7: Special exception for Step 4 (Idx 3)
    if (currentStepIdx === 3 && prog > 0.5) {
      torso.rotation.x = -15 * Math.PI/180;
      leftUpperArm.rotation.z = Math.PI/3; // 60 deg
      rightUpperArm.rotation.z = -Math.PI/3;
    }
    
    if (phaseTimer >= 0.15) {
      nextStep.mesh.scale.y = 1.0;
      startPhase('push');
    }
    
  } else if (phase === 'push') {
    // 0.3 seconds duration
    const prog = Math.min(1, phaseTimer / 0.3);
    
    updateWalkCycle();
    
    // Back leg straightens, body rises to new step height + offset
    const exactTargetY = nextStep.topY + 0.05;
    characterGroup.position.y = THREE.MathUtils.lerp(characterGroup.position.y, exactTargetY, prog);
    footBody.position.y = characterGroup.position.y; // sync physics up
    
    // Sway left/right struggling
    torso.rotation.z = Math.sin(prog * Math.PI * 2) * (4 * Math.PI/180);
    
    // Recover arms from step 4 fall
    if (currentStepIdx === 3) {
      torso.rotation.x = THREE.MathUtils.lerp(-15 * Math.PI/180, 0, prog);
      leftUpperArm.rotation.z = THREE.MathUtils.lerp(Math.PI/3, 30*Math.PI/180, prog);
      rightUpperArm.rotation.z = THREE.MathUtils.lerp(-Math.PI/3, -30*Math.PI/180, prog);
    }
    
    if (phaseTimer >= 0.3) {
      torso.rotation.z = 0;
      startPhase('recover');
    }
    
  } else if (phase === 'recover') {
    // 0.5 seconds duration pause
    const prog = phaseTimer / 0.5;
    
    // Heavy breathing scale logic (1.0 -> 1.03 -> 1.0 over 0.8s) simulated via sin
    const breath = 1.0 + (Math.sin(prog * Math.PI) * 0.03);
    torso.scale.set(1, breath, 1);
    
    if (phaseTimer >= 0.5) {
      torso.scale.set(1,1,1);
      
      if (currentStepIdx === 6) {
        startPhase('triumph');
      } else {
        currentStepIdx++;
        startPhase('reach');
      }
    }
    
  } else if (phase === 'triumph') {
    // Part 9 sequence 
    // 0-0.3: Lean forward catch
    // 0.3-0.7: Straighten up
    // 0.7-1.7: Arms raise + particles
    // 1.7-3.2: Look L/R + Hold
    // 3.2-4.2: Fade Out
    
    if (phaseTimer < 0.3) {
       torso.rotation.x = 10 * Math.PI/180;
    } else if (phaseTimer < 0.7) {
       const prog = (phaseTimer - 0.3) / 0.4;
       torso.rotation.x = THREE.MathUtils.lerp(10 * Math.PI/180, 0, prog);
    } else if (phaseTimer < 1.7) {
       const prog = (phaseTimer - 0.7) / 1.0;
       leftUpperArm.rotation.z = THREE.MathUtils.lerp(30*Math.PI/180, 70*Math.PI/180, prog);
       rightUpperArm.rotation.z = THREE.MathUtils.lerp(-30*Math.PI/180, -70*Math.PI/180, prog);
       leftUpperArm.rotation.x = 0;
       rightUpperArm.rotation.x = 0;
       
       if (!particles.userData.active) triggerParticles();
       
    } else if (phaseTimer < 2.5) {
       // Look left then right
       const subT = (phaseTimer - 1.7) / 0.8;
       head.rotation.y = Math.sin(subT * Math.PI * 2) * (10 * Math.PI/180);
    } else if (phaseTimer > 3.2 && phaseTimer < 4.2) {
       // Fade out
       const op = 1.0 - (phaseTimer - 3.2) / 1.0;
       characterGroup.traverse(child => {
         if (child.isMesh) child.material.opacity = op;
         child.material.transparent = true;
       });
    } else if (phaseTimer >= 4.2) {
       // Restart
       resetCharacterToStep(0);
       characterGroup.traverse(child => {
         if (child.isMesh) child.material.opacity = 1;
       });
       startPhase('reach');
    }
  }
};

const updateParticles = (dt) => {
  if (!particles.userData.active) return;
  particles.userData.age += dt;
  if (particles.userData.age > 1.0) {
    particles.material.opacity = Math.max(0, 1 - (particles.userData.age - 1.0) * 2);
    if (particles.userData.age > 1.5) {
      particles.userData.active = false;
      const positions = particles.geometry.attributes.position.array;
      for(let i=0; i<positions.length; i++) positions[i] = 0;
      particles.geometry.attributes.position.needsUpdate = true;
    }
  }
  
  const positions = particles.geometry.attributes.position.array;
  for(let i = 0; i < positions.length / 3; i++) {
    positions[i*3] += particles.userData.velocities[i*3] * dt;
    positions[i*3+1] += particles.userData.velocities[i*3+1] * dt;
    positions[i*3+2] += particles.userData.velocities[i*3+2] * dt;
  }
  particles.geometry.attributes.position.needsUpdate = true;
};

const onWindowResize = () => {
  if (!renderer || !camera) return;
  const container = renderer.domElement.parentElement;
  if (!container) return;
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
  labelRenderer.setSize(container.clientWidth, container.clientHeight);
};

const animate = () => {
  if (!isPlaying) return;
  requestAnimationFrame(animate);
  const dt = clock.getDelta();
  
  // Physics step
  world.step(1/60, dt, 3);
  
  processStateMachine(dt);
  updateParticles(dt);
  
  // Update Point Lights decay
  for (let i=0; i<pointLights.length; i++) {
    const p = pointLights[i];
    if (p.timer > 0) {
      p.timer -= dt;
      p.light.intensity = Math.max(0, p.timer * 4.0); // full intensity 4 fading down
    }
  }
  
  // Cinematic orbit
  const time = clock.getElapsedTime();
  camera.position.x = Math.sin(time * 0.05) * 8 - 4;
  camera.position.z = Math.cos(time * 0.05) * 8 + 4;
  camera.lookAt(0, 2, 0);

  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
};
