import axios from "axios";
import type { Request, Response } from "express";

export async function processFile(req: Request, res: Response){
    try{

        const file = req.file as Express.Multer.File;
        if(!file){
            return res.status(400).json({error: "No file uploaded"});
        }
        const fileBuffer = file.buffer;
        const response = await axios.post(
            "http://localhost:8000/report",
            fileBuffer,
            {
                headers: {
                    "Content-Type": "text/csv"
                }
            }
        );
        console.log("RESPONSE FROM PY: ", response);
        res.json(response.data);
    }catch(error){
        res.status(500).json({ error: "Processing failed" });
    }
}