import controllers.MainWindowController;
import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.layout.AnchorPane;
import javafx.stage.Stage;
import sun.applet.Main;

public class main extends Application {

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage primaryStage) throws Exception {
        Stage mainStage = new Stage();

        Parent root = FXMLLoader.load(getClass().getResource("/resources/view/MainWindowView.fxml"));

        Scene mainScene = new Scene(root,400,400);
        mainStage.setScene(mainScene);
        mainStage.show();
    }
}
