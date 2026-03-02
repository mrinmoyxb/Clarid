import "dotenv/config";
import express from "express";
import dataRouter from "./src/routes/data.route";
import cors from "cors";

const app = express();

app.use(cors({
  origin: "*", 
  methods: ["GET", "POST"],
}));
app.use(express.json());
app.use(express.urlencoded({extended: false}));

app.use("/api/v1/", dataRouter);

export default app;