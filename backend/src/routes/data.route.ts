import { Router } from "express";
import multer from "multer";
import { processFile } from "../controllers/data.controller";

const router = Router();
const upload = multer({storage: multer.memoryStorage()});
router.post("/report", upload.single("file"), processFile);

export default router;