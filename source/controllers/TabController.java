package controllers;

public abstract class TabController {
    MainWindowController parent;

    public TabController(MainWindowController parent){
        this.parent = parent;
    }
}
