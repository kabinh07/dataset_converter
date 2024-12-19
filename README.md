
# Dataset Converter: Step-by-Step Guide

## **1. Configuration**
1. Configure the `configs/config.yaml` file.
2. Create a `.env` file where you will save the annotator api url and token. 
3. Copy your main images directory into the `main_files` directory.  
   For example, check the [README file in main_files](https://github.com/kabinh07/dataset_converter/main_files/README.md).
4. Install the dependencies from `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

---

## **2. Running Operations**

### **2.1 Checking Projects**
To check available projects, run:

```bash
python3 main.py checkprojects
```

### **2.2 Downloading Projects**
To download a specific project, use:

```bash
python3 main.py download --project <id>
```

Replace `<id>` with the project ID you want to download.

### **2.3 Building Formatted Files**
To build the formatted files, run:

```bash
python main.py build
```

### **2.4 Drawing Bounding Boxes**
To draw bounding boxes, execute:

```bash
python main.py draw
```

---

**Note:**  
This project is currently under development. Contributions and feedback are welcome!
