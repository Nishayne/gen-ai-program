const jsonServer = require("json-server");
const server = jsonServer.create();
const router = jsonServer.router("db.json");
const middlewares = jsonServer.defaults();

server.use(middlewares);
server.use(jsonServer.bodyParser); // Enable JSON body parsing

// Middleware: Authorization Check
server.use((req, res, next) => {
  if (req.headers.authorization) {
    const token = req.headers.authorization.split(" ")[1];
    const users = router.db.get("auth.users").value();
    const user = users.find((u) => u.token === token);

    if (user) {
      req.user = user;
      return next();
    } else {
      return res.status(401).json({ error: "Invalid token" });
    }
  }

  if (req.path.startsWith("/api/auth/login")) {
    return next();
  }

  return res.status(403).json({ error: "Authorization required" });
});

// **POST /api/auth/login**
server.post("/api/auth/login", (req, res) => {
  const { email, password } = req.body;
  const users = router.db.get("auth.users").value();
  const user = users.find((u) => u.email === email && u.password === password);

  if (user) {
    return res.json({
      token: user.token,
      user: { id: user.id, role: user.role },
    });
  }
  return res.status(401).json({ error: "Invalid credentials" });
});

// **GET /api/auth/me**
server.get("/api/auth/me", (req, res) => {
  if (!req.user) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  return res.json({ id: req.user.id, name: req.user.name, role: req.user.role });
});

// **POST /api/lms/leave/approve**
server.post("/api/lms/leave/approve", (req, res) => {
  if (!req.user || req.user.role !== "manager") {
    return res.status(403).json({ error: "Access denied" });
  }

  const { leaveId, status } = req.body;
  const db = router.db;
  const leaveApplications = db.get("lms.leaveApplications").value();
  const leaveIndex = leaveApplications.findIndex((leave) => leave.id === leaveId);

  if (leaveIndex === -1) {
    return res.status(404).json({ error: "Leave request not found" });
  }

  leaveApplications[leaveIndex].status = status;
  db.write(); // Save changes

  return res.json({
    message: `Leave request ${status}`,
    status: status,
  });
});

// **GET /api/pods/details**
server.get("/api/pods/details", (req, res) => {
  const podDetails = router.db.get("pods.details").value();
  if (!podDetails) {
    return res.status(404).json({ error: "No pod details found" });
  }
  return res.json(podDetails);
});

// **GET /api/pods/recommend**
server.get("/api/pods/recommend", (req, res) => {
    console.log("here");
    const podRecommendations = router.db.get("pods.recommendations").value();
    if (!podRecommendations) {
      return res.status(404).json({ error: "No pod recommendations found" });
    }
    return res.json(podRecommendations);
  });

  
// **POST /api/pods/recommend**
server.post("/api/pods/recommend", (req, res) => {
  const { podId, recommendedUserId } = req.body;
  if (!podId || !recommendedUserId) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  const db = router.db;
  const recommendations = db.get("pods.recommendations").value();
  const pod = recommendations.find((p) => p.podId === podId);

  if (!pod) {
    return res.status(404).json({ error: "Pod not found" });
  }

  pod.members.push({ id: recommendedUserId, name: `User ${recommendedUserId}`, role: "Recommended Member" });
  db.write();

  return res.json({ message: "Recommendation sent successfully" });
});

// Use default router
server.use(router);

// Start Server
server.listen(3000, () => {
  console.log("JSON Server with custom routes running on port 3000");
});
