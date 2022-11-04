<?php
    include("Config.php");
        session_start();
        
        $username = $_POST['uname'];  
        $password = $_POST['passw'];  
            
        //to prevent from mysqli injection  
        $sql = "SELECT * FROM profiles WHERE Username = '". $username . "' and Password = '". $password . "';";
            
        $result = $con->query($sql);
            
        if($result->num_rows > 0){  
            header("Location: http://127.0.0.1:5000/");
        }  
        else{  
            echo "<h1> Login failed. Invalid username or password.</h1>";  
        }
?>
