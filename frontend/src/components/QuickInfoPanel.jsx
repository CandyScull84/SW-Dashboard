import "./QuickInfoPanel.css";

export default function QuickInfoPanel() {
    return (
        <aside className="quickinfo__panel">
            <div className="quickinfo__header">
                <h2 className="quickinfo__title">Quick Info</h2>
            </div>

            <div className="quickinfo__list">
                <div className="quickinfo__item">
                    <span className="dot" />
                    Pipelines updated every 60s
                </div>

                <div className="quickinfo__item">
                    <span className="dot" />
                    Merge Requests auto-refresh every 60s
                </div>

                <div className="quickinfo__item">
                    <span className="dot" />
                    Carousel rotates every 10s
                </div>

                <div className="quickinfo__item">
                    <span className="dot" />
                    Autoscroll enabled – disable in header for manual scrolling
                </div>

                <div className="quickinfo__item">
                    <span className="dot" />
                    Switch between light and dark mode, button in header
                </div>

                <div className="quickinfo__item hint">
                    More features will appear here...
                </div>
            </div>
        </aside>
    );
}