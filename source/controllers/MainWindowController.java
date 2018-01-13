package controllers;

import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.layout.AnchorPane;

import java.io.IOException;

public class MainWindowController {
    @FXML
    AnchorPane offers, account;
    OfferTabController offerTabController;
    AccountTabController accountTabController;

    public MainWindowController(){
        offerTabController = new OfferTabController(this);
        accountTabController = new AccountTabController(this);
    }

    @FXML
    protected void initialize() throws IOException{
        // Loads the offer menu
        FXMLLoader offerLoader = new FXMLLoader(getClass().getResource("/resources/view/OfferTabView.fxml"));
        offerLoader.setController(offerTabController);
        offers=offerLoader.load();
        // Loads the account menu
        FXMLLoader accountLoader = new FXMLLoader(getClass().getResource("/resources/view/AccountTabView.fxml"));
        accountLoader.setController(accountTabController);
        account=accountLoader.load();
    }
}
