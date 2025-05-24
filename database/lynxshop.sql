-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: lynxshop
-- ------------------------------------------------------
-- Server version	5.5.5-10.4.32-MariaDB

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
-- Table structure for table `categorias`
--

DROP TABLE IF EXISTS `categorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias` (
  `id_categoria` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias`
--

LOCK TABLES `categorias` WRITE;
/*!40000 ALTER TABLE `categorias` DISABLE KEYS */;
INSERT INTO `categorias` VALUES (1,'Bebidas','Todo tipo de bebidas'),(2,'Snacks','Botanas, galletas ...'),(3,'Golosinas','Chocolates y dulces...'),(4,'Frutas','Frutas frescas'),(5,'Papeleria','Útiles escolares..');
/*!40000 ALTER TABLE `categorias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detallepedido`
--

DROP TABLE IF EXISTS `detallepedido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detallepedido` (
  `id_detalle` int(11) NOT NULL AUTO_INCREMENT,
  `id_pedido` int(11) NOT NULL,
  `id_producto` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `id_pedido` (`id_pedido`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `detallepedido_ibfk_1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `detallepedido_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=191 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detallepedido`
--

LOCK TABLES `detallepedido` WRITE;
/*!40000 ALTER TABLE `detallepedido` DISABLE KEYS */;
INSERT INTO `detallepedido` VALUES (11,11,1,2,31.00),(20,25,1,2,31.00),(26,30,1,5,77.50),(29,32,1,1,15.50),(31,34,1,4,62.00),(35,36,1,1,15.50),(39,39,1,1,15.50),(41,41,1,3,46.50),(46,45,1,1,15.50),(60,55,1,1,15.50),(102,103,1,1,15.50),(113,111,1,2,31.00),(116,112,1,2,31.00),(123,116,1,6,93.00),(124,117,11,5,100.00),(126,118,1,4,62.00),(128,119,1,1,15.50),(130,120,1,3,46.50),(131,121,1,1,15.50),(132,122,1,2,31.00),(133,122,8,1,20.50),(134,122,11,2,40.00),(135,123,1,1,15.50),(138,125,1,1,15.50),(139,126,7,1,18.00),(140,127,15,1,20.00),(141,127,14,1,12.00),(142,127,18,1,5.10),(143,128,8,1,20.50),(144,129,8,2,24.00),(145,130,1,1,20.00),(146,130,11,3,135.00),(147,130,8,1,12.00),(148,131,8,1,12.00),(149,132,7,1,18.00),(150,133,1,1,20.00),(151,134,7,1,18.00),(152,135,7,1,18.00),(153,136,12,1,19.00),(154,137,12,1,19.00),(155,138,1,1,20.00),(156,139,1,1,20.00),(157,140,1,1,20.00),(158,141,19,1,28.00),(159,142,19,1,28.00),(160,142,22,1,20.00),(161,143,1,18,360.00),(162,144,37,1,19.00),(163,144,36,1,16.00),(164,144,33,1,5.00),(165,144,41,1,3.00),(166,144,46,1,7.00),(167,145,31,1,19.00),(168,146,11,1,45.00),(169,146,24,1,15.50),(170,146,59,1,27.00),(171,147,27,1,36.00),(172,148,50,1,7.00),(173,148,49,1,25.00),(174,149,7,1,18.00),(175,150,19,1,28.00),(176,151,11,1,45.00),(177,152,30,1,25.00),(178,153,21,1,10.00),(179,154,22,1,20.00),(180,155,47,1,2.00),(181,156,38,1,8.00),(182,157,46,3,21.00),(183,158,37,1,19.00),(184,158,36,1,16.00),(185,158,41,1,3.00),(186,159,13,1,18.00),(187,160,43,2,20.00),(188,160,39,3,15.00),(189,161,26,3,46.50),(190,162,17,1,19.00);
/*!40000 ALTER TABLE `detallepedido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estadospedidos`
--

DROP TABLE IF EXISTS `estadospedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estadospedidos` (
  `id_estado` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id_estado`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estadospedidos`
--

LOCK TABLES `estadospedidos` WRITE;
/*!40000 ALTER TABLE `estadospedidos` DISABLE KEYS */;
INSERT INTO `estadospedidos` VALUES (4,'Aceptado'),(3,'Cancelado'),(2,'Entregado'),(1,'Pendiente');
/*!40000 ALTER TABLE `estadospedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventorylog`
--

DROP TABLE IF EXISTS `inventorylog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventorylog` (
  `id_log` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `id_producto` int(11) NOT NULL,
  `nombre_producto` varchar(255) DEFAULT NULL,
  `cantidad_cambio` int(11) NOT NULL,
  `stock_anterior` int(11) NOT NULL,
  `stock_nuevo` int(11) NOT NULL,
  `razon` varchar(50) NOT NULL,
  `id_pedido` int(11) DEFAULT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_log`),
  KEY `id_producto` (`id_producto`),
  KEY `id_pedido` (`id_pedido`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `inventorylog_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `inventorylog_ibfk_2` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`),
  CONSTRAINT `inventorylog_ibfk_3` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventorylog`
--

LOCK TABLES `inventorylog` WRITE;
/*!40000 ALTER TABLE `inventorylog` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventorylog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nombres`
--

DROP TABLE IF EXISTS `nombres`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nombres` (
  `id_nombre` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellidoP` varchar(70) NOT NULL,
  `apellidoM` varchar(70) DEFAULT NULL,
  PRIMARY KEY (`id_nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=94 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nombres`
--

LOCK TABLES `nombres` WRITE;
/*!40000 ALTER TABLE `nombres` DISABLE KEYS */;
INSERT INTO `nombres` VALUES (1,'Juan Uribe','Pérez','Gómez'),(2,'Luis Rafael','Gómez',NULL),(3,'Carlos López','López','Martínez'),(4,'Laura','Méndez',NULL),(5,'Pedro','Fernández','Ramírez'),(6,'Usuario','Invitado',NULL),(7,'luis','puente','quevedo'),(8,'luis','puente','quevedo'),(9,'Usuario','De','Prueba'),(10,'Usuario','De','Prueba'),(11,'Admin','Test','Usuario'),(12,'Cliente','Prueba','Test'),(13,'Usuario','Emergencia','Test'),(14,'luis','puente','quevedo'),(15,'guest_1747365809478','',''),(16,'guest_1747366030418','',''),(17,'guest_1747366246671','',''),(18,'guest_1747366303797','',''),(19,'guest_1747366331048','',''),(20,'guest_1747366349500','',''),(21,'guest_1747366499610','',''),(22,'guest_1747366575294','',''),(23,'guest_1747366622447','',''),(24,'guest_1747366754753','',''),(25,'guest_1747366877980','',''),(26,'guest_1747366961679','',''),(27,'guest_1747369554174','',''),(28,'guest_1747371651895','',''),(29,'guest_1747371808057','',''),(30,'guest_1747372787546','',''),(31,'guest_1747372801028','',''),(32,'guest_1747373351456','',''),(33,'guest_1747373540881','',''),(34,'guest_1747373567365','',''),(35,'guest_1747373664760','',''),(36,'guest_1747373758221','',''),(37,'guest_1747373767389','',''),(38,'guest_1747373914181','',''),(39,'guest_1747373982699','',''),(40,'guest_1747374019677','',''),(41,'guest_1747374029360','',''),(42,'guest_1747374077657','',''),(43,'guest_1747374293993','',''),(44,'guest_1747374351158','',''),(45,'guest_1747374413442','',''),(46,'guest_1747375160874','',''),(47,'guest_1747375176055','',''),(48,'guest_1747375255445','',''),(49,'guest_1747375395683','',''),(50,'guest_1747421426141','',''),(51,'guest_1747422064078','',''),(52,'guest_1747528464411','',''),(53,'guest_1747529654994','',''),(54,'guest_1747530360294','',''),(55,'guest_1747530442710','',''),(56,'guest_1747531844339','',''),(57,'guest_1747532184979','',''),(58,'guest_1747532639646','',''),(59,'guest_1747532869846','',''),(60,'guest_1747532998501','',''),(61,'Admin','LynxShop',NULL),(62,'guest_1747535138046','',''),(63,'guest_1747541938035','',''),(64,'guest_1747542122911','',''),(65,'guest_1747542567730','',''),(66,'guest_1747543439004','',''),(67,'guest_1747584858358','',''),(68,'guest_1747597753628','',''),(69,'guest_1747598984455','',''),(70,'guest_1747611733487','',''),(71,'Coca-Cola','Admin','sd'),(72,'Coca-Cola','Admin','sd'),(73,'guest_1747620562451','',''),(74,'guest_1747621138292','',''),(75,'guest_1747681127084','',''),(76,'Franco','Escamilla','Clevedo'),(77,'guest_1747682209388','',''),(78,'Manuel','Hernández','Jácome'),(79,'guest_1748060350700','',''),(80,'guest_1748099774046','',''),(81,'guest_1748100719533','',''),(82,'guest_1748103514456','',''),(83,'luis','puente','quevedo'),(84,'luis','puente','quevedo'),(85,'luis','puente','quevedo'),(86,'dfv','dgvfsfgv','fv'),(87,'bn','vhj','bj'),(88,'bn','vhj','bj'),(89,'bn','vhj','bj'),(90,'guest_1748112216613','',''),(91,'guest_1748112996962','',''),(92,'guest_1748113150601','',''),(93,'guest_1748115991024','','');
/*!40000 ALTER TABLE `nombres` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedidos`
--

DROP TABLE IF EXISTS `pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos` (
  `id_pedido` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `fecha` datetime DEFAULT current_timestamp(),
  `estado` varchar(20) DEFAULT 'pendiente',
  `id_estado` int(11) NOT NULL DEFAULT 1,
  `nombre_completo` varchar(100) DEFAULT NULL,
  `telefono_contacto` varchar(20) DEFAULT NULL,
  `informacion_adicional` text DEFAULT NULL,
  `metodo_pago` varchar(20) DEFAULT 'efectivo',
  `total` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_pedido`),
  KEY `id_usuario` (`id_usuario`),
  KEY `fk_estado_pedido` (`id_estado`),
  CONSTRAINT `fk_estado_pedido` FOREIGN KEY (`id_estado`) REFERENCES `estadospedidos` (`id_estado`) ON UPDATE CASCADE,
  CONSTRAINT `pedidos_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=163 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidos`
--

LOCK TABLES `pedidos` WRITE;
/*!40000 ALTER TABLE `pedidos` DISABLE KEYS */;
INSERT INTO `pedidos` VALUES (11,6,'2024-12-09 23:09:20','pendiente',1,NULL,NULL,NULL,'efectivo',31.00),(12,7,'2024-12-09 23:09:20','pendiente',1,NULL,NULL,NULL,'efectivo',75.00),(13,9,'2024-12-09 23:09:20','pendiente',2,NULL,NULL,NULL,'efectivo',10.00),(14,10,'2024-12-09 23:09:20','pendiente',3,NULL,NULL,NULL,'efectivo',12.00),(15,8,'2024-12-09 23:09:20','pendiente',1,NULL,NULL,NULL,'efectivo',NULL),(16,10,'2024-12-15 21:56:56','pendiente',1,NULL,NULL,NULL,'efectivo',NULL),(20,11,'2024-12-16 17:37:30','pendiente',1,NULL,NULL,NULL,'efectivo',50.00),(21,11,'2024-12-16 17:38:18','pendiente',1,NULL,NULL,NULL,'efectivo',32.00),(22,11,'2024-12-16 17:39:50','pendiente',1,NULL,NULL,NULL,'efectivo',25.00),(23,11,'2024-12-16 17:42:17','pendiente',1,NULL,NULL,NULL,'efectivo',24.00),(24,11,'2024-12-16 21:45:26','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(25,11,'2024-12-16 21:51:21','pendiente',1,NULL,NULL,NULL,'efectivo',31.00),(26,11,'2024-12-16 21:51:35','pendiente',1,NULL,NULL,NULL,'efectivo',20.00),(27,11,'2024-12-16 21:57:45','pendiente',1,NULL,NULL,NULL,'efectivo',24.00),(28,11,'2024-12-16 22:17:33','pendiente',1,NULL,NULL,NULL,'efectivo',50.00),(29,11,'2024-12-16 22:17:54','pendiente',1,NULL,NULL,NULL,'efectivo',16.00),(30,11,'2025-01-03 09:14:24','pendiente',1,NULL,NULL,NULL,'efectivo',85.50),(31,11,'2025-01-03 09:15:14','pendiente',1,NULL,NULL,NULL,'efectivo',20.00),(32,11,'2025-02-05 14:48:50','pendiente',1,NULL,NULL,NULL,'efectivo',65.50),(33,11,'2025-02-05 14:53:44','pendiente',1,NULL,NULL,NULL,'efectivo',24.00),(34,11,'2025-02-11 12:41:49','pendiente',1,NULL,NULL,NULL,'efectivo',72.00),(35,11,'2025-02-11 13:03:03','pendiente',1,NULL,NULL,NULL,'efectivo',75.00),(36,11,'2025-03-21 09:55:35','pendiente',1,NULL,NULL,NULL,'efectivo',56.50),(37,11,'2025-03-21 09:59:38','pendiente',1,NULL,NULL,NULL,'efectivo',16.00),(39,19,'2025-05-15 20:39:07','pendiente',1,NULL,NULL,NULL,'efectivo',40.50),(40,11,'2025-05-15 21:23:29','pendiente',1,NULL,NULL,NULL,'efectivo',50.00),(41,11,'2025-05-15 21:27:10','pendiente',1,NULL,NULL,NULL,'efectivo',71.50),(42,11,'2025-05-15 21:30:46','pendiente',1,NULL,NULL,NULL,'efectivo',20.00),(43,11,'2025-05-15 21:31:43','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(44,11,'2025-05-15 21:32:11','pendiente',1,NULL,NULL,NULL,'efectivo',30.00),(45,11,'2025-05-15 21:32:29','pendiente',1,NULL,NULL,NULL,'efectivo',112.50),(46,11,'2025-05-15 21:35:00','pendiente',1,NULL,NULL,NULL,'efectivo',75.00),(47,11,'2025-05-15 21:36:15','pendiente',1,NULL,NULL,NULL,'efectivo',30.00),(48,11,'2025-05-15 21:37:02','pendiente',1,NULL,NULL,NULL,'efectivo',25.00),(49,11,'2025-05-15 21:39:14','pendiente',1,NULL,NULL,NULL,'efectivo',50.00),(50,11,'2025-05-15 21:41:18','pendiente',1,NULL,NULL,NULL,'efectivo',50.00),(51,11,'2025-05-15 21:42:41','pendiente',1,NULL,NULL,NULL,'efectivo',58.00),(52,31,'2025-05-15 21:45:20','pendiente',1,NULL,NULL,NULL,'efectivo',25.00),(53,31,'2025-05-15 21:47:40','pendiente',1,NULL,NULL,NULL,'efectivo',20.00),(54,31,'2025-05-15 21:51:39','pendiente',1,NULL,NULL,NULL,'efectivo',20.00),(55,31,'2025-05-15 21:53:31','pendiente',1,NULL,NULL,NULL,'efectivo',15.50),(56,19,'2025-05-15 21:55:22','pendiente',1,NULL,NULL,NULL,'efectivo',30.00),(57,19,'2025-05-15 21:59:31','pendiente',1,NULL,NULL,NULL,'efectivo',25.00),(58,11,'2025-05-15 22:25:54','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(59,32,'2025-05-15 22:26:10','pendiente',1,NULL,NULL,NULL,'efectivo',100.00),(60,19,'2025-05-15 22:26:43','pendiente',1,NULL,NULL,NULL,'efectivo',20.00),(61,19,'2025-05-15 22:32:25','pendiente',1,NULL,NULL,NULL,'efectivo',75.00),(62,19,'2025-05-15 22:42:26','pendiente',1,NULL,NULL,NULL,'efectivo',50.00),(63,19,'2025-05-15 22:46:36','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(64,19,'2025-05-15 22:47:21','pendiente',1,NULL,NULL,NULL,'efectivo',20.00),(65,19,'2025-05-15 22:48:39','pendiente',1,NULL,NULL,NULL,'efectivo',20.00),(66,19,'2025-05-15 22:51:13','pendiente',1,NULL,NULL,NULL,'efectivo',20.00),(67,19,'2025-05-15 22:51:57','pendiente',1,NULL,NULL,NULL,'efectivo',30.00),(68,19,'2025-05-15 22:52:45','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(69,19,'2025-05-15 22:55:56','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(70,19,'2025-05-15 22:56:56','pendiente',1,NULL,NULL,NULL,'efectivo',25.00),(71,19,'2025-05-15 23:00:22','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(74,34,'2025-05-15 23:03:37','pendiente',1,NULL,NULL,NULL,'efectivo',50.00),(75,19,'2025-05-15 23:04:55','pendiente',1,NULL,NULL,NULL,'efectivo',20.00),(76,19,'2025-05-15 23:07:32','pendiente',1,NULL,NULL,NULL,'efectivo',20.00),(83,10,'2025-05-15 23:51:03','pendiente',1,NULL,NULL,NULL,'efectivo',85.00),(84,10,'2025-05-15 23:51:14','pendiente',1,NULL,NULL,NULL,'efectivo',85.00),(85,10,'2025-05-15 23:51:52','pendiente',1,NULL,NULL,NULL,'efectivo',85.00),(86,10,'2025-05-15 23:52:19','pendiente',1,NULL,NULL,NULL,'efectivo',85.00),(87,10,'2025-05-15 23:52:51','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(88,10,'2025-05-15 23:52:59','pendiente',1,NULL,NULL,NULL,'efectivo',50.00),(89,10,'2025-05-15 23:53:23','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(90,10,'2025-05-15 23:56:39','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(91,10,'2025-05-15 23:57:31','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(92,10,'2025-05-15 23:57:53','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(93,10,'2025-05-15 23:58:27','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(96,53,'2025-05-16 00:01:18','pendiente',1,NULL,NULL,NULL,'efectivo',25.00),(97,53,'2025-05-16 00:01:50','pendiente',1,NULL,NULL,NULL,'efectivo',8.00),(98,54,'2025-05-16 00:04:15','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(99,54,'2025-05-16 00:05:58','pendiente',1,NULL,NULL,NULL,'efectivo',25.00),(100,54,'2025-05-16 00:06:59','pendiente',1,NULL,NULL,NULL,'efectivo',8.00),(101,19,'2025-05-16 00:11:43','pendiente',1,NULL,NULL,NULL,'efectivo',20.00),(102,19,'2025-05-16 00:14:32','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(103,55,'2025-05-16 12:52:55','pendiente',1,NULL,NULL,NULL,'efectivo',51.50),(104,56,'2025-05-16 13:02:21','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(105,57,'2025-05-17 18:42:43','pendiente',1,NULL,NULL,NULL,'efectivo',100.00),(106,19,'2025-05-17 18:44:09','pendiente',1,NULL,NULL,NULL,'efectivo',40.00),(107,58,'2025-05-17 18:55:06','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(108,58,'2025-05-17 18:56:04','pendiente',1,NULL,NULL,NULL,'efectivo',30.00),(109,58,'2025-05-17 19:03:13','pendiente',1,NULL,NULL,NULL,'efectivo',10.00),(110,60,'2025-05-17 19:08:44','cancelado',3,'Luis Angel Puente Quevedo','2444484749','en las canchas\n','cash',10.00),(111,68,'2025-05-17 19:59:59','cancelado',3,NULL,NULL,NULL,'cash',61.00),(112,68,'2025-05-17 21:01:21','entregado',2,NULL,NULL,NULL,'cash',91.00),(113,72,'2025-05-17 22:30:17','pendiente',1,'Luis Angel Puente Quevedo','2444484749','dvzc','cash',10.00),(114,72,'2025-05-17 22:30:54','pendiente',1,'Luis Angel Puente Quevedo','2444484749','xc','cash',30.00),(115,19,'2025-05-18 11:02:37','pendiente',1,NULL,NULL,NULL,'efectivo',234.00),(116,68,'2025-05-18 13:22:54','pendiente',1,NULL,NULL,NULL,'efectivo',138.00),(117,68,'2025-05-18 13:29:09','pendiente',1,NULL,NULL,NULL,'efectivo',100.00),(118,68,'2025-05-18 13:59:56','pendiente',1,NULL,NULL,NULL,'efectivo',72.00),(119,68,'2025-05-18 14:01:54','entregado',2,NULL,NULL,NULL,'efectivo',25.50),(120,80,'2025-05-18 20:10:00','cancelado',3,'Luis Angel x','2444484749','sd','efectivo',86.50),(121,82,'2025-05-19 12:59:56','entregado',2,'Luis Angel Perez Arguets','2444484745','iygergi8fsoadkpoif','efectivo',15.50),(122,84,'2025-05-19 13:19:13','pendiente',1,'Felipe Angeles','2223481711','En CC','efectivo',91.50),(123,85,'2025-05-19 13:29:41','pendiente',1,NULL,NULL,NULL,'efectivo',27.50),(124,85,'2025-05-19 13:30:10','pendiente',1,NULL,NULL,NULL,'efectivo',30.00),(125,68,'2025-05-19 16:37:08','pendiente',1,NULL,NULL,NULL,'efectivo',15.50),(126,68,'2025-05-23 18:58:21','cancelado',3,NULL,NULL,NULL,'efectivo',18.00),(127,68,'2025-05-23 18:58:43','entregado',2,NULL,NULL,NULL,'efectivo',37.10),(128,68,'2025-05-23 18:59:15','entregado',2,NULL,NULL,NULL,'efectivo',20.50),(129,68,'2025-05-23 22:14:47','entregado',2,NULL,NULL,NULL,'efectivo',24.00),(130,68,'2025-05-23 22:27:47','pendiente',1,NULL,NULL,NULL,'efectivo',167.00),(131,68,'2025-05-23 22:28:03','pendiente',1,NULL,NULL,NULL,'efectivo',12.00),(132,68,'2025-05-23 22:28:30','cancelado',3,NULL,NULL,NULL,'efectivo',18.00),(133,68,'2025-05-23 22:43:01','pendiente',1,NULL,NULL,NULL,'efectivo',20.00),(134,68,'2025-05-23 22:43:22','pendiente',1,NULL,NULL,NULL,'efectivo',18.00),(135,68,'2025-05-23 22:43:38','pendiente',1,NULL,NULL,NULL,'efectivo',18.00),(136,68,'2025-05-23 22:45:17','entregado',2,NULL,NULL,NULL,'efectivo',19.00),(137,68,'2025-05-23 22:45:32','entregado',2,NULL,NULL,NULL,'efectivo',19.00),(138,68,'2025-05-23 22:45:48','entregado',2,NULL,NULL,NULL,'efectivo',20.00),(139,68,'2025-05-23 22:50:15','entregado',2,NULL,NULL,NULL,'efectivo',20.00),(140,68,'2025-05-23 22:57:03','entregado',2,NULL,NULL,NULL,'efectivo',20.00),(141,68,'2025-05-23 23:10:15','entregado',2,NULL,NULL,NULL,'efectivo',28.00),(142,68,'2025-05-23 23:10:57','entregado',2,NULL,NULL,NULL,'efectivo',48.00),(143,68,'2025-05-23 23:12:15','cancelado',3,NULL,NULL,NULL,'efectivo',360.00),(144,92,'2025-05-24 10:36:23','pendiente',1,NULL,NULL,NULL,'efectivo',50.00),(145,92,'2025-05-24 10:37:22','pendiente',1,NULL,NULL,NULL,'efectivo',19.00),(146,92,'2025-05-24 10:38:26','pendiente',1,NULL,NULL,NULL,'efectivo',87.50),(147,92,'2025-05-24 10:40:05','pendiente',1,NULL,NULL,NULL,'efectivo',36.00),(148,92,'2025-05-24 10:41:23','pendiente',1,NULL,NULL,NULL,'efectivo',32.00),(149,92,'2025-05-24 10:41:58','pendiente',1,NULL,NULL,NULL,'efectivo',18.00),(150,68,'2025-05-24 12:38:49','pendiente',1,NULL,NULL,NULL,'efectivo',28.00),(151,97,'2025-05-24 12:45:15','pendiente',1,'Cliente invitado','2223481711','vf','efectivo',45.00),(152,68,'2025-05-24 12:47:54','aceptado',4,NULL,NULL,NULL,'efectivo',25.00),(153,99,'2025-05-24 13:00:10','pendiente',1,'Cliente invitado','41',NULL,'efectivo',10.00),(154,99,'2025-05-24 13:02:36','aceptado',4,'Cliente invitado','2444484749',NULL,'efectivo',20.00),(155,68,'2025-05-24 13:35:37','pendiente',1,NULL,NULL,NULL,'efectivo',2.00),(156,68,'2025-05-24 13:38:01','pendiente',1,NULL,NULL,NULL,'efectivo',8.00),(157,68,'2025-05-24 13:38:20','pendiente',1,NULL,NULL,NULL,'efectivo',21.00),(158,68,'2025-05-24 13:38:52','pendiente',1,NULL,NULL,NULL,'efectivo',38.00),(159,68,'2025-05-24 13:39:10','pendiente',1,NULL,NULL,NULL,'efectivo',18.00),(160,68,'2025-05-24 13:39:26','aceptado',4,NULL,NULL,NULL,'efectivo',35.00),(161,68,'2025-05-24 13:39:42','aceptado',4,NULL,NULL,NULL,'efectivo',46.50),(162,68,'2025-05-24 13:40:12','pendiente',1,NULL,NULL,NULL,'efectivo',19.00);
/*!40000 ALTER TABLE `pedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `id_categoria` int(11) NOT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_producto`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `id_categoria` (`id_categoria`),
  CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,'Coca-Cola 600 ml ',20.00,6,1,'coca-coca-600.jpg'),(7,'Limonada 600 ml',18.00,17,1,'valleLimonada.jpg'),(8,'Doritos Dinamita 50g',12.00,2,2,'DoritosDinamita.jpg'),(11,'Red Bull Sin Azúcar',45.00,12,1,'redbull.jpg'),(12,'Naranjada 600 ml',19.00,22,1,'valleNaranjada.jpg'),(13,'Agua Mineral 600 ml',18.00,15,1,'peñafiel.jpg'),(14,'Agua Natural 1L',12.00,15,1,'aguaciel.jpg'),(15,'Té Negro Limón 600 ml',20.00,17,1,'fuzetealimon.jpg'),(16,'Boing Mango 500 ml',14.50,19,1,'boingmango.jpg'),(17,'Coca-Cola 600 ml sin azúcar',19.00,21,1,'cocasinazucar.jpg'),(18,'Sprite 355 ml',5.10,23,1,'spritemini.jpg'),(19,'Powerade Moras 1L',28.00,22,1,'powerade.jpg'),(20,'Crujitos Fuego 59g',10.00,16,2,'Crujitosfuegos.jpg'),(21,'Fritos Sal y Limón 79g',10.00,20,2,'FritosLimon.jpg'),(22,'Karate Japonés 127g',20.00,14,2,'KarateCacahuate.jpg'),(23,'Cheetos Mix 55g',13.00,0,2,'cheetosmix.jpg'),(24,'Oreo Original 144g',15.50,10,2,'oreo.jpg'),(25,'Emperador Senzo 93g',10.00,0,2,'EmperadorSenzo.jpg'),(26,'B-ready Nutella 22g',15.50,10,3,'nutellabready.jpg'),(27,'Susalia Flama 200g',36.00,11,2,'susalia.jpg'),(28,'Flor de Naranjo 75g',10.00,12,2,'florNaranjo.jpg'),(29,'Freskas Caramelos 35g',21.00,10,3,'freskas.jpg'),(30,'Trident Canela 30.6g',25.00,22,3,'trindetcanela.jpg'),(31,'Dulcigomas 68g',19.00,17,3,'dulcigomas.jpg'),(32,'Paleta Rockaleta 24g',7.00,15,3,'Rockaleta.jpg'),(33,'Mazapan 28g',5.00,28,3,'Mazapan.jpg'),(34,'Pelon Pelo Rico 35g',11.50,11,3,'pelonrico.jpg'),(35,'Paletón Bombón 25g',10.00,14,3,'paleton.jpg'),(36,'Pelón Ricatira 29g',16.00,21,3,'ricatira.jpg'),(37,'Panditas Originales 45g',19.00,14,3,'panditas.jpg'),(38,'Manzana Roja',8.00,6,4,'ManzanaRoja.jpg'),(39,'Guayaba',5.00,11,4,'Guayaba.jpg'),(40,'Pera',8.00,9,4,'Pera.jpg'),(41,'Plátano Dominico',3.00,14,4,'PlatanoDominico.jpg'),(42,'Ciruela',7.00,7,4,'ciruela.jpg'),(43,'Mango',10.00,9,4,'Mango.jpg'),(44,'Durazno',8.00,7,4,'Durazno.jpg'),(45,'Mamey',25.00,3,4,'Mamey.jpg'),(46,'Mandarina',7.00,7,4,'Mandarina.jpg'),(47,'Limón',2.00,12,4,'Limon.jpg'),(48,'Manzana Golden',10.00,8,4,'ManzanaGolden.jpg'),(49,'Pastisetas Galletas 90g',25.00,11,2,'pastisetas.jpg'),(50,'Bolígrafo Negro',7.00,20,5,'Boligrafo.jpg'),(51,'Bolígrafo Rojo',7.00,21,5,'bolirojo.jpg'),(52,'Marcador Pizarrón Negro',35.00,10,5,'Marcador.jpg'),(53,'Bic Puntillas',25.00,4,5,'puntillas.jpg'),(54,'Marcatexto 2 pack',36.00,4,5,'Marcatextos.jpg'),(55,'Bolígrafos Fashion',36.00,5,5,'FashioBoli.jpg'),(56,'Sharpie Marcador 3 pack',75.00,10,5,'Sharpie.jpg'),(57,'Bic Boligrafos Up',36.00,12,5,'boliup.jpg'),(58,'Cuaderno Argollado',45.00,11,5,'Cuaderno.jpg'),(59,'Cuaderno Rayado',27.00,14,5,'cuadernorayado.jpg');
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id_rol` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id_rol`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (2,'Administrador'),(1,'Cliente'),(3,'Invitado'),(5,'Usuario');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `id_nombre` int(11) DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `contraseña` varchar(255) DEFAULT NULL,
  `id_rol` int(11) NOT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  `plain_password` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `correo` (`correo`),
  UNIQUE KEY `telefono` (`telefono`),
  KEY `id_nombre` (`id_nombre`),
  KEY `id_rol` (`id_rol`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`id_nombre`) REFERENCES `nombres` (`id_nombre`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id_rol`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (6,1,'juan.perez@example.com','5551234567','$2a$10$X7H1QALRRxX9Q1Y4z8P5h.fGxmAw/1xn0R9SWzw1zrg9n8cvJw8hy',1,'2024-12-09 22:37:14',NULL),(7,2,'ana.gomez@example.com','5559876543','$2a$10$4XMM5dZ4zMVK5KJN9XZMzu3ZQdaF2TYi5xYzB0H5f8.URVKad0hFa',2,'2024-12-09 22:37:14',NULL),(8,3,'carlos.lopez@example.com','5557891234','$2a$10$PoLSg6KfLUQBgDRYm/1B6eH3QphcV7EwkuS3lkBUU8J5zQvbNSJCa',1,'2024-12-09 22:37:14',NULL),(9,4,'laura.mendez@example.com','5556549870','$2a$10$XeDqLsm6jXHPHU9UcMzCke4kcgYZnZ5BG.fFQi8i/mB.x2uWa0yxu',2,'2024-12-09 22:37:14',NULL),(10,5,'pedro.fernandez@example.com','5553214569','$2a$10$CcUNzwGZE.JGz/p8.nHjReg.DmdOJoFDimqO6RE.y5fxQ2cUgHIjK',3,'2024-12-09 22:37:14',NULL),(11,6,'guest@lynxshop.com','0000000000',NULL,3,'2024-12-16 09:55:57',NULL),(12,7,'juanitoperez@example.com','2444484749','$2a$10$gKubJxh..j8A06H7tiYBcOruUW5hHokPUSzCyUv9qd6dn2/3k.4ea',1,'2025-05-15 18:49:45',NULL),(13,8,'juanperez@example.com','2444444444','$2a$10$BWvl03MtU7loJSU7a6lL9e9vyK8npqxFnZPyMWnOFxk3klpz8REh6',1,'2025-05-15 18:54:24',NULL),(16,11,'admin.test@example.com','5559999999','$2a$10$JsVRc5dJhcf/qtvnpL3Zte2qdcY6D9j4xyKhvzMNNV0p84uvLRA8K',2,'2025-05-15 19:25:58',NULL),(17,12,'cliente.prueba@example.com','5557777777','$2a$10$HfzIhGCCaxqyaIdGgjARSuOKAcm1Uy82YfLuNaajn6JrjLWy9Sj/2',1,'2025-05-15 19:27:33',NULL),(18,13,'emergencia@test.com','5551112222','no-bcrypt',2,'2025-05-15 19:34:30','Admin123'),(19,14,'emergencia2@test.com','1111111111','$2a$10$pbMB54alVuelqKWyMteibuc5wDgPGpPwBGUUNq/7SdPA7eGbP9vOy',1,'2025-05-15 19:56:20',NULL),(20,15,'guest_1747365809478@lynxshop.com','0005809478','$2a$10$bz2xVL8snWzii/x7Gmn1r.BwNVpXh5N76tljMItvR/fj6bcH668ru',3,'2025-05-15 21:23:29',NULL),(21,16,'guest_1747366030418@lynxshop.com','0006030418','$2a$10$lBC9irD/dY9VXcrr9GFDlOS3ziK8u0JZlquMN0r8Bm7A81Bw/p8n6',3,'2025-05-15 21:27:10',NULL),(22,17,'guest_1747366246671@lynxshop.com','0006246671','$2a$10$qZjm6EUTFQrjqmcxVlDSR.co/22wGJ3TmTUyozqx0XiZlNZJPwqq.',3,'2025-05-15 21:30:46',NULL),(23,18,'guest_1747366303797@lynxshop.com','0006303797','$2a$10$uifDQt1VkXzSB.ZEr1F.Jucnl7.NEFe4xKBKkYpEkRxtEsZEqy0Da',3,'2025-05-15 21:31:43',NULL),(24,19,'guest_1747366331048@lynxshop.com','0006331048','$2a$10$0QcpW4rpj5oHp.vdukjuMudebPZFqiVMuzg81j7HBbCxzs2qaqvGu',3,'2025-05-15 21:32:11',NULL),(25,20,'guest_1747366349500@lynxshop.com','0006349500','$2a$10$Y0mCm0RZ3gv7mVXHe.ni0ONiG17KEwynRvNWtrViI/82fpehcmYNO',3,'2025-05-15 21:32:29',NULL),(26,21,'guest_1747366499610@lynxshop.com','0006499610','$2a$10$7vItYHqQojiuO3yyqNDh0.v/iOv3cLcpQTSsGEpymYKOPTbC8.fRK',3,'2025-05-15 21:35:00',NULL),(27,22,'guest_1747366575294@lynxshop.com','0006575294','$2a$10$Tm3S3AcybJGqyMPfYyR4eOkibvhvAuOiGTNEp885nkYU6.AUixi82',3,'2025-05-15 21:36:15',NULL),(28,23,'guest_1747366622447@lynxshop.com','0006622447','$2a$10$NFABPlzoPRdc5KtG0lvt1uJtR.j1mmlrQQBpWsiUeGh2mso1VH7Hm',3,'2025-05-15 21:37:02',NULL),(29,24,'guest_1747366754753@lynxshop.com','0006754753','$2a$10$bEt3On68SPjYDOINjptLnu6ijmy8kpugWh8tFw9s3gLtPXyjCqzbm',3,'2025-05-15 21:39:14',NULL),(30,25,'guest_1747366877980@lynxshop.com','0006877980','$2a$10$aGmZUmYxY6KEvvVJMZEZ6ORx8tYrYggwD.ybJsByGZWESXz5CxDum',3,'2025-05-15 21:41:18',NULL),(31,26,'guest_1747366961679@lynxshop.com','0006961679','$2a$10$S8yk3sBnQD5RBDdZ3hXkBOeoD8/ZFjZ/fpfxnEiAAPj3naV33/7iu',3,'2025-05-15 21:42:41',NULL),(32,27,'guest_1747369554174@lynxshop.com','0009554174','$2a$10$9oxzApf7spOI5Izgin9YKusIFXq9VSjFZ6lA0u35WHorrLMPvrwc.',3,'2025-05-15 22:25:54',NULL),(33,28,'guest_1747371651895@lynxshop.com','0001651895','$2a$10$RUj2pDAkRHj4sQkCIwMOj.jaVVBdRJ9f7dbwudXcWkiN3I0ijEgzC',3,'2025-05-15 23:00:52',NULL),(34,29,'guest_1747371808057@lynxshop.com','0001808057','$2a$10$AYuM4vP6cn5uXUVGPVdwkOt.XbPuvP4zDPAhCin49ia0euv132sXq',3,'2025-05-15 23:03:28',NULL),(35,30,'guest_1747372787546@lynxshop.com','0002787546','$2a$10$/pBtSqN9p/OVHHDSWyHtMeF9ief1K2iS3TKIaOMR0g11RuImV8tzm',3,'2025-05-15 23:19:47',NULL),(36,31,'guest_1747372801028@lynxshop.com','0002801028','$2a$10$Odmn9Lby1dsKaO7nWDwNUOaC1YEJboMRBSfNPVg/UmkXARQnsocTe',3,'2025-05-15 23:20:01',NULL),(37,32,'guest_1747373351456@lynxshop.com','0003351456','$2a$10$NQ5rDciQlBdVyPikVKf8GeD.PDb6j47XAtK8eFrNxWCL760QpqtwO',3,'2025-05-15 23:29:11',NULL),(38,33,'guest_1747373540881@lynxshop.com','0003540881','$2a$10$D8IBik20tm5ftoIz5HV17exYDGWPTvuecWXdKq2YKk8gx6E1K9laS',3,'2025-05-15 23:32:21',NULL),(39,34,'guest_1747373567365@lynxshop.com','0003567365','$2a$10$1IF28Tqe3kuv69rH.oBS3uR1ItMJtkm9NTvQSLUbgLMO11/yw7Pga',3,'2025-05-15 23:32:47',NULL),(40,35,'guest_1747373664760@lynxshop.com','0003664760','$2a$10$iUho9liMGqsugFUyxEMHr.t3ROw6jyZii.Wo3vr/CTPB08ZmwBKri',3,'2025-05-15 23:34:24',NULL),(41,36,'guest_1747373758221@lynxshop.com','0003758221','$2a$10$.JyNHDUCR36UiyCLOJ3jh.FFjrCxzJO4GlIxFT1VVxxBH1zBrqibi',3,'2025-05-15 23:35:58',NULL),(42,37,'guest_1747373767389@lynxshop.com','0003767389','$2a$10$KFvdgOkF5vIA6GOHjOWrUeVdwO8hm6JsaMH3UqfD1cUxz44Gz0zla',3,'2025-05-15 23:36:07',NULL),(43,38,'guest_1747373914181@lynxshop.com','0003914181','$2a$10$uAzSZB60Dm.APz2QpIp5LeyNVhG0uIdA2q57pI4ZMIzQ6Haa6t0pe',3,'2025-05-15 23:38:34',NULL),(44,39,'guest_1747373982699@lynxshop.com','0003982699','$2a$10$KxxAyPjlkmVQ2UzRyIZb3OyCxia5fbfkuNzT0b5PieRiklnSbiCom',3,'2025-05-15 23:39:42',NULL),(45,40,'guest_1747374019677@lynxshop.com','0004019677','$2a$10$..f8hO8xA6w/3Qn1V5BMh.MnFmGxssqCB4ohpFdW4umzwJ9EebuAG',3,'2025-05-15 23:40:19',NULL),(46,41,'guest_1747374029360@lynxshop.com','0004029360','$2a$10$ripDbbmaDf6IoMxOy2ExO.caYYzj.qojejxxQLx.RybK9ywEd0bmO',3,'2025-05-15 23:40:29',NULL),(47,42,'guest_1747374077657@lynxshop.com','0004077657','$2a$10$JUiLZKj.M6qFzN2WpVGD0.sEtuX0Wgda0.ip2HhAzd5DlF0N5E9iK',3,'2025-05-15 23:41:17',NULL),(48,43,'guest_1747374293993@lynxshop.com','0004293993','$2a$10$nc1HYNCHLw4OV/sivMTnFuIpU23eMwXj89l00YkyKWp5bQclYfyGK',3,'2025-05-15 23:44:54',NULL),(49,44,'guest_1747374351158@lynxshop.com','0004351158','$2a$10$w9bhYV3OqaYlWjm/9.Mp/uxN51VZ.7zhaqWcW5Y4Ya5sTrfqIsUk.',3,'2025-05-15 23:45:51',NULL),(50,45,'guest_1747374413442@lynxshop.com','0004413442','$2a$10$tGfqgSJkj9sxloY6ekhe9.UtlxXTgWRyxLCCAI9GgCIKBH02panGS',3,'2025-05-15 23:46:53',NULL),(51,46,'guest_1747375160874@lynxshop.com','0005160874','$2a$10$pEZAry6KN/1AJF9gp3ki1O2uKuILoNKAnjUzo2r9hk9Qr.CsHKkh.',3,'2025-05-15 23:59:21',NULL),(52,47,'guest_1747375176055@lynxshop.com','0005176055','$2a$10$MDdlfqyxrX1YCMxSa7iQjuQ1lSsLgOKrAbgROgc7F34Oc1EXv0oTG',3,'2025-05-15 23:59:36',NULL),(53,48,'guest_1747375255445@lynxshop.com','0005255445','$2a$10$6uj3Hguxm2KAgRKivx3KqeK2EEBp9gLISKaUe5qGerUKInDOnCLkS',3,'2025-05-16 00:00:56',NULL),(54,49,'guest_1747375395683@lynxshop.com','0005395683','$2a$10$rC0lm6Lct4REIEGcLYKCRu5H4c23yaTBKOmzdZngN83mhllnkj/Vy',3,'2025-05-16 00:03:15',NULL),(55,50,'guest_1747421426141@lynxshop.com','0001426141','$2a$10$kEceNLv2rCF.F0WJTxiuoeHy.M1vZJpvQ8S1Vpl3eOA82OEgbx/Fy',3,'2025-05-16 12:50:26',NULL),(56,51,'guest_1747422064078@lynxshop.com','0002064078','$2a$10$i2IyNDwOCw54R8CgAzy8qexUF.5eP0TPli3f1Zf6n3NJu2YMgEFnC',3,'2025-05-16 13:01:04',NULL),(57,52,'guest_1747528464411@lynxshop.com','0008464411','$2a$10$I4qkeivt.1FeKQ3WMJ4cQ.sZs7Q3CogkIO7TG9N/1lC.ljIYv3yKy',3,'2025-05-17 18:34:24',NULL),(58,53,'guest_1747529654994@lynxshop.com','0009654994','$2a$10$zWxxvlYbZmj2IYAF8eQ9a.vSWS.YblDar7vXMtmfDHQiPlxjbKLX.',3,'2025-05-17 18:54:15',NULL),(59,54,'guest_1747530360294@lynxshop.com','0000360294','$2a$10$6QURZ2GGshTj4zFY6f9Ek.wricPuA4xb1ucSLj.25beJrg2k1pnUC',3,'2025-05-17 19:06:00',NULL),(60,55,'guest_1747530442710@lynxshop.com','0000442710','$2a$10$4FcMICLbiDV3SqZaA1Xq8eNNgKroSg5pYW/g7VHeunZlvvQQY/oOS',3,'2025-05-17 19:07:22',NULL),(61,56,'guest_1747531844339@lynxshop.com','0001844339','$2a$10$OJzMV2rCDaNDyw2LvLVhKepxI8fcKcWYjysRnSG99p3ihr1FoXDgi',3,'2025-05-17 19:30:44',NULL),(62,57,'guest_1747532184979@lynxshop.com','0002184979','$2a$10$xcsrt.kAPrISC494k1mW/egx.7Q9IHzL9vvMUmcHibDYrxq.6xdzO',3,'2025-05-17 19:36:25',NULL),(63,58,'guest_1747532639646@lynxshop.com','0002639646','$2a$10$nLwFNTGSGysVRA1/1YkGX.UXW/L7n/LbuaoD.he6ePrsaFe8pdiQm',3,'2025-05-17 19:43:59',NULL),(64,59,'guest_1747532869846@lynxshop.com','0002869846','$2a$10$r2elHxRonTslJkcy.M3DE.iQWVs1xphFmpzrBt1LJUfADH0JqDkIa',3,'2025-05-17 19:47:50',NULL),(65,60,'guest_1747532998501@lynxshop.com','0002998501','$2a$10$hfhq7T5CwQDz0O/RO0g2LO1oMdyQRKYBzY0COQAq8iWbRleFEcjHu',3,'2025-05-17 19:49:58',NULL),(68,6,'admin@lynxshop.com','9876543210','Admin1234',2,'2025-05-17 19:57:19',NULL),(69,62,'guest_1747535138046@lynxshop.com','0005138046','$2a$10$AoWv52NW0vcO60vir8KdWu3whF98segkkwR.rk1owcw2FTfD6TUwm',3,'2025-05-17 20:25:38',NULL),(70,63,'guest_1747541938035@lynxshop.com','0001938035','$2a$10$RyJsm6TOLA2cCiLrkLW1uei/cRKU0f25iqHDsrciXPUPB/43UJ4OW',3,'2025-05-17 22:18:59',NULL),(71,64,'guest_1747542122911@lynxshop.com','0002122911','$2a$10$/uDa4AC7mCcVOerc9FKXOu/6vtvcdiVIa.3tKjB8RBh.RW.vb1wne',3,'2025-05-17 22:22:03',NULL),(72,65,'guest_1747542567730@lynxshop.com','0002567730','$2a$10$AWCMCGt7XmOtghHm1xJefe5wBRhsDpiCt.j9TjSjzDn96JrvmoemO',3,'2025-05-17 22:29:28',NULL),(73,66,'guest_1747543439004@lynxshop.com','0003439004','$2a$10$bmerQHgDu9y8uZoMmhQHCO/d0Q2z9QNh7tnSMBEprCdMft.m7oqXq',3,'2025-05-17 22:43:59',NULL),(74,67,'guest_1747584858358@lynxshop.com','0004858358','$2a$10$RtCFtR5sKOOjyAFxQ8Rwyu.P5u6xqc/pSU00YIS20PvmfnY0dRNkS',3,'2025-05-18 10:14:18',NULL),(75,68,'guest_1747597753628@lynxshop.com','0007753628','$2a$10$bBK7etMLkPdsQkqdZcuQU.JQWVWYUHqch5/o9oKA9BVqeiNKShaIK',3,'2025-05-18 13:49:13',NULL),(76,69,'guest_1747598984455@lynxshop.com','0008984455','$2a$10$BXw4Wya8RVf2EiizG9h3LOri08Jp7OVfUNIqmQftynwa6b8oh0Wu2',3,'2025-05-18 14:09:45',NULL),(77,70,'guest_1747611733487@lynxshop.com','0001733487','$2a$10$MVgpU7pSfNWLHXvD1VnkkOtbIMOzmHCJKAUux6N/a6B4PN7c5J8I2',3,'2025-05-18 17:42:13',NULL),(79,72,'admin@lynxshosp.com','2444484744','$2a$10$n7CnXxzCjDRXZTlF/hIkhuE6AynJ3128Uya1GzYoe9yh8tWOzyKli',1,'2025-05-18 18:45:35',NULL),(80,73,'guest_1747620562451@lynxshop.com','0000562451','$2a$10$MBTnkksFs.CQnQ.ax7Xo2.RL.n0jzZK0CaZnmzzhQprXiniqkxA3W',3,'2025-05-18 20:09:22',NULL),(81,74,'guest_1747621138292@lynxshop.com','0001138292','$2a$10$1ZU4mpeIBuH2.Vk/jjzTsOV797KXUb5F/scpLcNEK8/pyZ3NAXMnK',3,'2025-05-18 20:18:58',NULL),(82,75,'guest_1747681127084@lynxshop.com','2444484745','$2a$10$PZBzx8VO4tAX1XbJQuDVe.REfGl5UoDrCzUYIYkFvmzoo7x.XXK7O',3,'2025-05-19 12:58:47',NULL),(83,76,'123@gmail.com','2441234567','$2a$10$Xs8YRRGhTs/hiNeDJBBVi.Rh6y4yfCPqfCHpHFTbLRxKHApU0k2d2',1,'2025-05-19 13:04:09',NULL),(84,77,'guest_1747682209388@lynxshop.com','2223481711','$2a$10$fzQzvT9Ddinnb9voCymjm.rvE0AmrM3Rs4kiMbt.eheXUke8ihUHe',3,'2025-05-19 13:16:49',NULL),(85,78,'jacome@gmail.com.mx','2223111814','$2a$10$BUfALMQotEJsE151gPNlROoeXuFGLzY4ALIvoXDdrn760L.15J3BW',1,'2025-05-19 13:26:55',NULL),(86,79,'guest_1748060350700@lynxshop.com','0000350700','$2a$10$y0AjXvIYvdcB6XeC7MLRNewLKRJT4rcczfhlmAAk2HC.ik7AKDy5C',3,'2025-05-23 22:19:10',NULL),(87,80,'guest_1748099774046@lynxshop.com','0009774046','$2a$10$zA4nYTue9trc3WOSDd9VGem92zmSvtCrTsQCRM8GyXowetN4I0zaO',3,'2025-05-24 09:16:14',NULL),(88,81,'guest_1748100719533@lynxshop.com','0000719533','$2a$10$PkLiNad8JyMN/p3xkaDkMO1jPU6owSqEOLwPhE4dNKzfzVPdsCUI.',3,'2025-05-24 09:31:59',NULL),(89,82,'guest_1748103514456@lynxshop.com','0003514456','$2a$10$SW11lmEQI.W7I/xm9lyevuhkPcIrMU2qysXu3.V1eQ/paS3C7tGzm',3,'2025-05-24 10:18:34',NULL),(92,85,'admin1@lynxshop.com','2444475749','$2a$10$6UL5AHPYb3qpO/QmPj8hOOxg4QRZMlF3mRpjQ1dxK7TVLfSmYc8Yu',1,'2025-05-24 10:30:56',NULL),(97,90,'guest_1748112216613@lynxshop.com','0002216613','$2a$10$zxJbN1hrLa/WMGh4X5Mgj.z/gVk.QQyJHD5nXGkl8AEDLA.aeWfKe',3,'2025-05-24 12:43:36',NULL),(98,91,'guest_1748112996962@lynxshop.com','0002996962','$2a$10$.OpCtEPBZ7WpLi1/q9E2xO.f0vxyqQxjqcRWxubkjorEcJFeYw9hy',3,'2025-05-24 12:56:37',NULL),(99,92,'guest_1748113150601@lynxshop.com','41','$2a$10$zAvInYDd7V0RNeA/H6ynROo37en89JeOSk5EZcETPyBHep0f/7lLu',3,'2025-05-24 12:59:10',NULL),(100,93,'guest_1748115991024@lynxshop.com','0005991024','$2a$10$nQx/nmS0Rbi.nKsdLcFe0O4J4gr4EqbolthPcePdn5JHoPkPmHKDG',3,'2025-05-24 13:46:31',NULL);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-24 14:58:49
