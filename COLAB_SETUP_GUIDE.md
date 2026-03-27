# Google Colab Setup Guide for BERT Training

## Step 1: Prepare Files for Upload

Before opening Colab, gather these files in ONE folder on your local machine:

```
colab_inputs/
├── train_tensors.pt         (from data/processed/)
├── val_tensors.pt           (from data/processed/)
├── test_tensors.pt          (from data/processed/)
├── prep_config.json         (from data/processed/)
└── 04_bert_classification_colab.ipynb  (the notebook from notebooks/)
```

### Files to Upload (Total ~300MB):
- **data/processed/train_tensors.pt** — Training data
- **data/processed/val_tensors.pt** — Validation data
- **data/processed/test_tensors.pt** — Test data
- **data/processed/prep_config.json** — Model configuration
- **04_bert_classification_colab.ipynb** — Colab notebook (special version)

---

## Step 2: Open Google Colab & Upload Files

1. Go to [Google Colab](https://colab.research.google.com)
2. Click **File** → **New notebook**
3. Click **Runtime** → **Change runtime type** → Select **GPU** → **Save**
4. In the first cell, run:
   ```python
   from google.colab import files
   files.upload()
   ```
5. Upload the 4 data files + notebook

---

## Step 3: Run the Training

Open the uploaded notebook and run all cells. The notebook will:
- Automatically detect GPU (should see "cuda" device)
- Load your preprocessed tensors
- Fine-tune DistilBERT for 6 epochs (~5-10 minutes on T4 GPU)
- Generate visualizations and results

---

## Step 4: Download Results Back to Local System

After training completes, run the **Download Results** cell. This will download:

```
colab_outputs/
├── best_distilbert/          (complete model directory)
│   ├── config.json
│   ├── pytorch_model.bin     ← Model weights
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   └── vocab.txt
├── training_history.json     (metrics per epoch)
├── training_curves.png       (loss/accuracy/F1 plots)
├── confusion_matrix.png      (test set confusion matrix)
└── bert_results.json         (final test metrics)
```

---

## Step 5: Copy Results to Local Project

After downloading from Colab:

1. Extract `best_distilbert/` → `project1-document-ai/models/`
2. Copy `.json` and `.png` files → `project1-document-ai/logs/`

Your local project structure will now be:
```
project1-document-ai/
├── data/processed/ (already have these)
├── logs/
│   ├── training_history.json      ← NEW
│   ├── training_curves.png        ← NEW  
│   ├── confusion_matrix.png       ← NEW
│   └── bert_results.json          ← NEW
├── models/
│   └── best_distilbert/           ← NEW (from Colab)
│       ├── config.json
│       ├── pytorch_model.bin
│       └── ...
└── notebooks/
    ├── 04_bert_classification.ipynb (local version—don't need to update)
```

---

## Step 6: Continue Locally (Next Steps)

Once you have the trained model in `project1-document-ai/models/best_distilbert/`:

1. **Create inference notebook** (`05_inference.ipynb`)
   - Load best model
   - Test predictions on new text

2. **Deploy to Docker/API** 
   - Create Flask API endpoint
   - Wrap model for predictions

3. **Push to GitHub**
   - Commit trained model (or use Git LFS for large files)
   - Add README with results

---

## Troubleshooting

### File upload too slow?
- Increase file upload timeout: In Colab, go to **Tools** → **Settings** → **Notebook settings**
- Or upload directly to Google Drive and mount it

### GPU not available?
- Check Runtime → Manage sessions → Restart
- Verify Runtime type is set to GPU
- Try again

### Out of memory error?
- Reduce `BATCH_SIZE` in the notebook (currently 16)
- DistilBERT is lightweight (66M parameters) but still needs ~7GB VRAM for training

---

## Timeline Estimate

| Phase | Time |
|-------|------|
| Setup & upload | 5-10 min |
| Training (6 epochs) | 5-10 min (GPU) vs 30-60 min (CPU) |
| Download results | 2-3 min |
| **Total** | **~15-25 minutes** |

GPU is **3-6x faster** than CPU!
