import axios from "axios";
import FormData from "form-data";
import type { Request, Response } from "express";

export async function uploadFile(req: Request, res: Response){
    try{
        const file = req.file as Express.Multer.File;
        
        if(!file){
            return res.status(400).json({error: "No file uploaded"});
        }

        const formData = new FormData();
        formData.append("file", file.buffer, file.originalname);

        const fileBuffer = file.buffer;
        const response = await axios.post(
            "http://localhost:8000/upload",
            formData,
            {
                headers: formData.getHeaders()
            }
        );
        console.log("RESPONSE FROM PY: ", response);
        res.json(response.data);
    }catch(error){
        res.status(500).json({ error: "Processing failed" });
    }
}

export async function generateReport(req: Request, res: Response){
    try{
        const { dataset_id } = req.body;

        if(!dataset_id){
            return res.status(400).json({error: "Missing fields"});
        }

        const response = await axios.post(
            "http://localhost:8000/report",
            {
                dataset_id
            }
        )
        res.json(response.data)
    }catch(error){
        res.status(500).json({ error: "Couldn't generate failed" });
    }
}

export async function transformDataset(req: Request, res: Response){
    try{
        const { dataset_id, instruction } = req.body;

        if(!dataset_id || !instruction){
            return res.status(400).json({error: "Missing fields"});
        }

        const response = await axios.post(
            "http://localhost:8000/transform",
            {
                dataset_id,
                instruction
            }
        )
        res.json(response.data)
    }catch(error){
        res.status(500).json({ error: "Transformation failed" });
    }
}