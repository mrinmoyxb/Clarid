import "dotenv/config";
import express from "express";

import dataRouter from "./src/routes/data.route";

const app = express();

app.use(express.json());
app.use(express.urlencoded({extended: false}));

app.use("/api/v1/", dataRouter);

export default app;