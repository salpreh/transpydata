-- Source: https://gist.github.com/blewert/3b4b6a96bee032aefe20
--
-- Table structure for table `module`
--

CREATE TABLE IF NOT EXISTS `module` (
  `module_Id` varchar(16) NOT NULL,
  `module_name` varchar(255) NOT NULL,
  `credits` int(4) NOT NULL,
  PRIMARY KEY (`module_Id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `module`
--

INSERT INTO `module` (`module_Id`, `module_name`, `credits`) VALUES
('CS101', 'Introduction to Computing', 10),
('CS203', 'Data Structures and Algorithms', 10),
('CS204', 'Computer Architecture', 10),
('M101', 'Foundation Mathematics', 20);

-- --------------------------------------------------------

--
-- Table structure for table `registered`
--

CREATE TABLE IF NOT EXISTS `registered` (
  `student_Id` varchar(16) NOT NULL,
  `module_Id` varchar(16) NOT NULL,
  PRIMARY KEY (`student_Id`,`module_Id`),
  KEY `module_Id` (`module_Id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `registered`
--

INSERT INTO `registered` (`student_Id`, `module_Id`) VALUES
('S10345', 'CS101'),
('S10348', 'CS101'),
('S10346', 'CS203'),
('S10346', 'CS204'),
('S10347', 'CS204'),
('S10348', 'M101');

-- --------------------------------------------------------

--
-- Table structure for table `staff`
--

CREATE TABLE IF NOT EXISTS `staff` (
  `staff_Id` varchar(16) NOT NULL,
  `staff_name` varchar(128) NOT NULL,
  `staff_grade` varchar(128) NOT NULL,
  PRIMARY KEY (`staff_Id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `staff`
--

INSERT INTO `staff` (`staff_Id`, `staff_name`, `staff_grade`) VALUES
('E10010', 'Alan Turing', 'Senior Lecturer'),
('E10011', 'Tony Hoare', 'Reader'),
('E10012', 'Seymour Cray', 'Lecturer');

-- --------------------------------------------------------

--
-- Table structure for table `student`
--

CREATE TABLE IF NOT EXISTS `student` (
  `student_Id` varchar(16) NOT NULL,
  `student_name` varchar(128) NOT NULL,
  `degree_scheme` varchar(255) NOT NULL,
  PRIMARY KEY (`student_Id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `student`
--

INSERT INTO `student` (`student_Id`, `student_name`, `degree_scheme`) VALUES
('S10345', 'John Smith', 'BSc Computer Science'),
('S10346', 'Sian Evans', 'BSc Computer Science'),
('S10347', 'Sean Crossan', 'BSc Electronic Engineering'),
('S10348', 'Jamie McDonald', 'BSc Mathematics');

-- --------------------------------------------------------

--
-- Table structure for table `teaches`
--

CREATE TABLE IF NOT EXISTS `teaches` (
  `staff_Id` varchar(16) NOT NULL,
  `module_Id` varchar(16) NOT NULL,
  PRIMARY KEY (`staff_Id`,`module_Id`),
  KEY `fk_teaches_module` (`module_Id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `teaches`
--

INSERT INTO `teaches` (`staff_Id`, `module_Id`) VALUES
('E10010', 'CS101'),
('E10011', 'CS101'),
('E10011', 'CS203'),
('E10010', 'CS204'),
('E10012', 'CS204'),
('E10011', 'M101');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `registered`
--
ALTER TABLE `registered`
  ADD CONSTRAINT `fk_registered_module` FOREIGN KEY (`module_Id`) REFERENCES `module` (`module_Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_registered_student` FOREIGN KEY (`student_Id`) REFERENCES `student` (`student_Id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `teaches`
--
ALTER TABLE `teaches`
  ADD CONSTRAINT `fk_teaches_module` FOREIGN KEY (`module_Id`) REFERENCES `module` (`module_Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_teaches_staff` FOREIGN KEY (`staff_Id`) REFERENCES `staff` (`staff_Id`) ON DELETE CASCADE ON UPDATE CASCADE;
