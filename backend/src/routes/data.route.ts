import { Router } from "express";
import multer from "multer";
import { uploadFile, transformDataset, generateReport } from "../controllers/data.controller";

const router = Router();
const upload = multer({storage: multer.memoryStorage()});
router.post("/upload", upload.single("file"), uploadFile);
router.post("/report", generateReport);
router.post("/transform", transformDataset);

export default router;