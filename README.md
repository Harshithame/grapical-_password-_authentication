# AuthenX

Here are **clear and simple setup instructions** for running your **AuthenX project** locally using **XAMPP**:

---

# **AuthenX Setup Instructions (XAMPP)**

---

## **1. Install Required Software**

* [XAMPP](https://www.apachefriends.org/) – for PHP & MySQL
* [VS Code](https://code.visualstudio.com/) – to edit code
* [Git](https://git-scm.com/) – (optional, for pushing to GitHub)

---

## **2. Place Project in XAMPP Folder**

1. Download the AuthenX project (ZIP or from GitHub).
2. Extract the folder and rename it to `AuthenX`.
3. Move the folder to:

   ```
   C:\xampp\htdocs\AuthenX
   ```

---

## **3. Start Local Server**

1. Open **XAMPP Control Panel**.
2. Start **Apache** and **MySQL**.
3. Open browser and go to:

   ```
   http://localhost/AuthenX
   ```

---

## **4. Create Database**

1. Open **phpMyAdmin**:

   ```
   http://localhost/phpmyadmin
   ```
2. Click **New → Create database** and name it:

   ```
   authenx
   ```

---

## **5. Import or Create Tables**

Option A: **Import SQL file** (if included):

* Go to **Import → Choose File → Select `authenx.sql` → Go**

Option B: **Create manually** (run this query in SQL tab):

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone BIGINT NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_graphics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    image1 VARCHAR(255) NOT NULL,
    slice1 INT NOT NULL,
    image2 VARCHAR(255) NOT NULL,
    slice2 INT NOT NULL,
    image3 VARCHAR(255) NOT NULL,
    slice3 INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## **6. Configure Database Connection**

Edit `config/db.php` (or `db.php` in your root folder):

```php
<?php
$host = "localhost";
$user = "root";
$pass = "";
$dbname = "authenx";

$conn = new mysqli($host, $user, $pass, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
```

---

## **7. Run the Project**

* Open browser and go to:

```
http://localhost/AuthenX
```

* Test signup, login, and graphical password features.

---

## **8. Optional – Push to GitHub**

1. Open terminal in project folder:

   ```bash
   git init
   git add .
   git commit -m "Initial commit - AuthenX"
   git branch -M main
   git remote add origin https://github.com/<your-username>/AuthenX.git
   git push -u origin main
   ```

---

Do you want me to **add these setup instructions directly into your README file** (final version for GitHub)?
Or should I **give you a separate `SETUP.md` file** just for installation steps?
