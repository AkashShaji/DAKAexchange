package controllers;

import javafx.fxml.FXML;
import javafx.scene.layout.VBox;

public class OfferTabController extends TabController {
    @FXML VBox Offers;

    public OfferTabController(MainWindowController parent){
        super(parent);
    }
}
