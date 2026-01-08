import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


class PdfReport:
    def __init__(self, output_path: str, title: str = "Experiment report"):
        self.output_path = output_path
        self.title = title
        self.pages = []

    def add_text(self, text: str, fontsize: int = 12):
        fig, ax = plt.subplots(figsize=(11.7, 8.3))  # A4 landscape-ish
        ax.axis("off")
        ax.text(0.01, 0.99, text, va="top", ha="left", wrap=True, fontsize=fontsize)
        self.pages.append(fig)

    def add_figure(self, fig: plt.Figure):
        self.pages.append(fig)


    def add_dataframe(self, df, title: str, max_rows: int = 25):
        view = df.head(max_rows).copy()

        fig, ax = plt.subplots(figsize=(16, 6))
        ax.axis("off")
        ax.set_title(title, fontsize=12, pad=10)

        cols = list(view.columns)

        # Only: column widths (give "pokemons" more room if present)
        if "pokemons" in cols:
            col_widths = []
            for c in cols:
                if c == "pokemons":
                    col_widths.append(0.52)
                elif c in ("fitness", "stats_sum"):
                    col_widths.append(0.10)
                elif c == "run":
                    col_widths.append(0.06)
                elif c in ("solver", "winner"):
                    col_widths.append(0.08)
                else:
                    col_widths.append(0.08)

            s = sum(col_widths)
            col_widths = [w / s for w in col_widths]
        else:
            col_widths = None

        table = ax.table(
            cellText=view.values,
            colLabels=view.columns,
            loc="center",
            cellLoc="center",
            colWidths=col_widths,
        )

        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.3)

        if len(df) > max_rows:
            ax.text(
                0.01, 0.02,
                f"Showing first {max_rows} of {len(df)} rows",
                transform=ax.transAxes,
                fontsize=9,
            )

        self.pages.append(fig)

    def write(self):
        with PdfPages(self.output_path) as pdf:
            # tytułowa
            fig, ax = plt.subplots(figsize=(11.7, 8.3))
            ax.axis("off")
            ax.text(0.5, 0.6, self.title, ha="center", va="center", fontsize=22)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

            for fig in self.pages:
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)
