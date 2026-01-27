CREATE TABLE categorie (
  id_categorie INT AUTO_INCREMENT PRIMARY KEY,
  libelle VARCHAR(100) NOT NULL UNIQUE,
  stockable TINYINT(1) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE produit_sequence (
  id INT AUTO_INCREMENT PRIMARY KEY
) ENGINE=InnoDB;

CREATE TABLE produit (
  id_produit CHAR(8) PRIMARY KEY,
  nom_produit VARCHAR(255) NOT NULL,
  prix_achat DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (prix_achat >= 0),
  prix_vente_bouteille DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (prix_vente_bouteille >= 0),
  prix_vente_verre DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (prix_vente_verre >= 0),
  stock_actuel INT NOT NULL DEFAULT 0 CHECK (stock_actuel >= 0),
  unite_vente VARCHAR(20) NOT NULL DEFAULT 'bouteille' CHECK (unite_vente IN ('bouteille', 'verre')),
  id_categorie INT NOT NULL,
  CONSTRAINT ck_produit_id CHECK (id_produit REGEXP '^PR[0-9]{6}$'),
  CONSTRAINT fk_produit_categorie
    FOREIGN KEY (id_categorie) REFERENCES categorie (id_categorie)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE entree_stock (
  id_entree INT AUTO_INCREMENT PRIMARY KEY,
  date_entree DATE NOT NULL,
  quantite INT NOT NULL CHECK (quantite > 0),
  id_produit CHAR(8) NOT NULL,
  CONSTRAINT fk_entree_produit
    FOREIGN KEY (id_produit) REFERENCES produit (id_produit)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE vente (
  id_vente INT AUTO_INCREMENT PRIMARY KEY,
  date_vente DATE NOT NULL,
  quantite INT NOT NULL CHECK (quantite > 0),
  montant DECIMAL(10,2) NOT NULL CHECK (montant >= 0),
  nom_preparation VARCHAR(255),
  type_vente VARCHAR(20) NOT NULL CHECK (type_vente IN ('bouteille', 'verre')),
  id_produit CHAR(8) NULL,
  id_categorie INT NOT NULL,
  id_recu INT NOT NULL,
  CONSTRAINT fk_vente_produit
    FOREIGN KEY (id_produit) REFERENCES produit (id_produit)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk_vente_categorie
    FOREIGN KEY (id_categorie) REFERENCES categorie (id_categorie)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE recu (
  id_recu INT AUTO_INCREMENT PRIMARY KEY,
  date_recu DATETIME NOT NULL,
  nom_client VARCHAR(255)
) ENGINE=InnoDB;

ALTER TABLE vente
  ADD CONSTRAINT fk_vente_recu
  FOREIGN KEY (id_recu) REFERENCES recu (id_recu)
  ON DELETE RESTRICT
  ON UPDATE CASCADE;

CREATE TABLE charge (
  id_charge INT AUTO_INCREMENT PRIMARY KEY,
  type_charge VARCHAR(100) NOT NULL,
  montant DECIMAL(10,2) NOT NULL CHECK (montant >= 0),
  date_charge DATE NOT NULL
) ENGINE=InnoDB;

DELIMITER //
CREATE TRIGGER tr_produit_id
BEFORE INSERT ON produit
FOR EACH ROW
BEGIN
  DECLARE seq INT;
  IF NEW.id_produit IS NULL OR NEW.id_produit = '' THEN
    INSERT INTO produit_sequence VALUES (NULL);
    SET seq = LAST_INSERT_ID();
    IF seq > 999999 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Limite PR999999 atteinte';
    END IF;
    SET NEW.id_produit = CONCAT('PR', LPAD(seq, 6, '0'));
  END IF;
END//
DELIMITER ;

CREATE INDEX idx_entree_date ON entree_stock (date_entree);
CREATE INDEX idx_vente_date ON vente (date_vente);
CREATE INDEX idx_charge_date ON charge (date_charge);
CREATE INDEX idx_produit_categorie ON produit (id_categorie);
CREATE INDEX idx_vente_categorie ON vente (id_categorie);

INSERT INTO categorie (libelle, stockable) VALUES
('Vins moelleux', 1),
('Vins Bordeaux', 1),
('Vins rouges', 1),
('Vins mousseux', 1),
('Champagne', 1),
('Whisky', 1),
('Gins', 1),
('Liqueur', 1),
('Shooter', 1),
('Jus', 1),
('Eau', 1),
('Sirop', 1),
('Sucrerie', 1),
('Repas', 1),
('Cocktail', 0),
('Mocktail', 0);
