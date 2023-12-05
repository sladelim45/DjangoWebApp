import { $ } from "/static/jquery/src/jquery.js";

export function say_hi(elt) {
    console.log("Say hi to", elt);
}

say_hi($("h1"));

export function make_table_sortable(table) {
    console.log("called in main")
    const lastHeaderCell = table.find("th:last")
    lastHeaderCell.on("click", function() {
        if (lastHeaderCell.hasClass('sort-desc') || !lastHeaderCell.hasClass('sort-asc')) {
            console.log("sorting ascending")
            lastHeaderCell.removeClass('sort-desc').addClass('sort-asc');
            sortTable(table, "asc");
        } else {
            console.log("sorting descending")
            lastHeaderCell.removeClass('sort-asc').addClass('sort-desc');
            sortTable(table, "desc");
        }
    })
}

function sortTable(table, order) {
    const rows = table.find("tbody").find("tr").toArray();
    rows.sort(function(a, b) {
        const numA = getNumericValue($(a).find("td:last").text());
        const numB = getNumericValue($(b).find("td:last").text());
        if (order === "asc") {
            return numA - numB;
        } else {
            return numB - numA;
        }
    });
    $(rows).appendTo(table.find("tbody"));
}

function getNumericValue(text) {
    if (text.includes("%")) {
        return parseFloat(text.split("%")[0]);
    } else if (text.includes("/")) {
        return parseFloat(text.split("/")[0]);
    } else {
        return parseFloat(text);
    }
}