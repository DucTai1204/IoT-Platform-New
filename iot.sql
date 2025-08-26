-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: iot_data
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `du_lieu_thiet_bi`
--

DROP TABLE IF EXISTS `du_lieu_thiet_bi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `du_lieu_thiet_bi` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `thiet_bi_id` int NOT NULL,
  `khoa` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `gia_tri` text COLLATE utf8mb4_unicode_ci,
  `thoi_gian` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `thiet_bi_id` (`thiet_bi_id`,`thoi_gian`),
  CONSTRAINT `du_lieu_thiet_bi_ibfk_1` FOREIGN KEY (`thiet_bi_id`) REFERENCES `thiet_bi` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `du_lieu_thiet_bi`
--

LOCK TABLES `du_lieu_thiet_bi` WRITE;
/*!40000 ALTER TABLE `du_lieu_thiet_bi` DISABLE KEYS */;
INSERT INTO `du_lieu_thiet_bi` VALUES (1,1,'nhiet_do','27.5','2025-07-29 11:20:56'),(2,2,'trang_thai','on','2025-07-29 11:20:56');
/*!40000 ALTER TABLE `du_lieu_thiet_bi` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `khoa_du_lieu`
--

DROP TABLE IF EXISTS `khoa_du_lieu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `khoa_du_lieu` (
  `id` int NOT NULL AUTO_INCREMENT,
  `thiet_bi_id` int NOT NULL,
  `khoa` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `don_vi` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mo_ta` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `thiet_bi_id` (`thiet_bi_id`),
  CONSTRAINT `khoa_du_lieu_ibfk_1` FOREIGN KEY (`thiet_bi_id`) REFERENCES `thiet_bi` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `khoa_du_lieu`
--

LOCK TABLES `khoa_du_lieu` WRITE;
/*!40000 ALTER TABLE `khoa_du_lieu` DISABLE KEYS */;
INSERT INTO `khoa_du_lieu` VALUES (1,1,'nhiet_do','C','Nhiệt độ phòng'),(2,2,'trang_thai',NULL,'Trạng thái bật/tắt');
/*!40000 ALTER TABLE `khoa_du_lieu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log_rule`
--

DROP TABLE IF EXISTS `log_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `log_rule` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `rule_id` int DEFAULT NULL,
  `gia_tri_thuc_te` float DEFAULT NULL,
  `thoi_gian` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `rule_id` (`rule_id`),
  CONSTRAINT `log_rule_ibfk_1` FOREIGN KEY (`rule_id`) REFERENCES `rule_thiet_bi` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log_rule`
--

LOCK TABLES `log_rule` WRITE;
/*!40000 ALTER TABLE `log_rule` DISABLE KEYS */;
INSERT INTO `log_rule` VALUES (1,1,32.1,'2025-07-29 11:20:56');
/*!40000 ALTER TABLE `log_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nguoi_dung`
--

DROP TABLE IF EXISTS `nguoi_dung`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nguoi_dung` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ten` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mat_khau_hash` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `vai_tro` enum('admin','user') COLLATE utf8mb4_unicode_ci DEFAULT 'user',
  `ngay_tao` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nguoi_dung`
--

LOCK TABLES `nguoi_dung` WRITE;
/*!40000 ALTER TABLE `nguoi_dung` DISABLE KEYS */;
INSERT INTO `nguoi_dung` VALUES (1,'Admin','admin@example.com','hash_admin','admin','2025-07-29 11:20:56'),(2,'User1','user1@example.com','hash_user1','user','2025-07-29 11:20:56');
/*!40000 ALTER TABLE `nguoi_dung` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `node`
--

DROP TABLE IF EXISTS `node`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `node` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ten_node` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mo_ta` text COLLATE utf8mb4_unicode_ci,
  `vi_tri` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nguoi_quan_ly_id` int DEFAULT NULL,
  `ngay_tao` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `nguoi_quan_ly_id` (`nguoi_quan_ly_id`),
  CONSTRAINT `node_ibfk_1` FOREIGN KEY (`nguoi_quan_ly_id`) REFERENCES `nguoi_dung` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `node`
--

LOCK TABLES `node` WRITE;
/*!40000 ALTER TABLE `node` DISABLE KEYS */;
INSERT INTO `node` VALUES (1,'Node 1','Khu vực A','Tầng 1',1,'2025-07-29 11:20:56'),(2,'Node 2','Khu vực B','Tầng 2',2,'2025-07-29 11:20:56');
/*!40000 ALTER TABLE `node` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rule_thiet_bi`
--

DROP TABLE IF EXISTS `rule_thiet_bi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rule_thiet_bi` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ten_rule` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `field` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `operator` enum('>','>=','<','<=','=','!=') COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` float NOT NULL,
  `action_device_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_command` enum('turn_on','turn_off') COLLATE utf8mb4_unicode_ci NOT NULL,
  `muc_do_uu_tien` int DEFAULT '0',
  `trang_thai` enum('enabled','disabled') COLLATE utf8mb4_unicode_ci DEFAULT 'enabled',
  `ngay_tao` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `action_device_id` (`action_device_id`),
  CONSTRAINT `rule_thiet_bi_ibfk_1` FOREIGN KEY (`action_device_id`) REFERENCES `thiet_bi` (`ma_thiet_bi`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rule_thiet_bi`
--

LOCK TABLES `rule_thiet_bi` WRITE;
/*!40000 ALTER TABLE `rule_thiet_bi` DISABLE KEYS */;
INSERT INTO `rule_thiet_bi` VALUES (1,'Bật quạt khi nhiệt độ cao','nhiet_do','>',30,'TB002','turn_on',1,'enabled','2025-07-29 11:20:56');
/*!40000 ALTER TABLE `rule_thiet_bi` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `thiet_bi`
--

DROP TABLE IF EXISTS `thiet_bi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `thiet_bi` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ma_thiet_bi` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ten_thiet_bi` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `loai_thiet_bi` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `node_id` int DEFAULT NULL,
  `trang_thai` enum('online','offline','error') COLLATE utf8mb4_unicode_ci DEFAULT 'offline',
  `ngay_dang_ky` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ma_thiet_bi` (`ma_thiet_bi`),
  KEY `node_id` (`node_id`),
  CONSTRAINT `thiet_bi_ibfk_1` FOREIGN KEY (`node_id`) REFERENCES `node` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `thiet_bi`
--

LOCK TABLES `thiet_bi` WRITE;
/*!40000 ALTER TABLE `thiet_bi` DISABLE KEYS */;
INSERT INTO `thiet_bi` VALUES (1,'TB001','Cảm biến nhiệt độ','sensor',1,'online','2025-07-29 11:20:56'),(2,'TB002','Công tắc đèn','switch',2,'offline','2025-07-29 11:20:56');
/*!40000 ALTER TABLE `thiet_bi` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-01  7:15:21
