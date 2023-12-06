import { $ } from "/static/jquery/src/jquery.js";

export function say_hi(elt) {
    console.log("Say hi to", elt);
}

say_hi($("h1"));

export function make_table_sortable(table) {
    const sortableHeaders = table.find("th.sortable")
    sortableHeaders.on("click", function() {
        const currHeader = $(this);
        const colNum = currHeader.index();
        if (!currHeader.hasClass('sort-desc') && !currHeader.hasClass('sort-asc')) {
            console.log("sorting ascending")
            sortableHeaders.removeClass('sort-asc sort-desc');
            currHeader.removeClass('sort-desc').addClass('sort-asc');
            sortTable(table, "asc", colNum);
        } else if (currHeader.hasClass('sort-asc')) {
            console.log("sorting descending");
            sortableHeaders.removeClass('sort-asc sort-desc');
            currHeader.removeClass('sort-asc').addClass('sort-desc');
            sortTable(table, "desc", colNum);
        } else if (currHeader.hasClass('sort-desc')) {
            console.log("unsorting");
            currHeader.removeClass('sort-desc');
            sortableHeaders.removeClass('sort-asc sort-desc');
            sortTable(table, "unsorted", colNum);
        }
    })
}

function sortTable(table, order, colNum) {
    const rows = table.find("tbody").find("tr").toArray();
    rows.sort(function(a, b) {
        const numA = getNumericValue(String($(a).find(`td:eq(${colNum})`).data("value")));
        const numB = getNumericValue(String($(b).find(`td:eq(${colNum})`).data("value")));
        if (order === "asc") {
            return numA - numB;
        } else if (order === "desc") {
            return numB - numA;
        } else {
            return $(a).data("index") - $(b).data("index")
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

export function make_form_async(form) {
    form.on("submit", function(event) {
        event.preventDefault();
        const formData = new FormData($("form")[0]);
        form.find('input[type="file"]').prop('disabled', true);
        form.find('button[type="submit"]').prop('disabled', true);

        $.ajax ({
            url: form.attr("action"),
            type: "POST",
            data: formData,
            processData: false,
            contentTyle: false,
            mimeType: form.attr("enctye"),
            success: function(response) {
                form.replaceWith('Upload succeeded');
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        })
    })
}

export function make_grade_hypothesized(table){
    const hypothesizeButton = $("<button>").text("Hypothesize").insertBefore(table);
    hypothesizeButton.on("click", function() {
        if (table.hasClass("hypothesized")) {
            table.removeClass("hypothesized");
            hypothesizeButton.text("Hypothesize");

            const numberInputs = table.find("td:has(:input.hypothesized-grade)");
            numberInputs.each(function() {
                const originalText = $(this).data("originalText");
                $(this).data("value", originalText)
                $(this).html(originalText);
            })
            grade_computation(table);
        } else {
            table.addClass("hypothesized");
            hypothesizeButton.text("Actual grades");

            const targetRows = table.find("td:contains('Not Due'), td:contains('Ungraded')");
            targetRows.each(function() {
                const originalText = $(this).text();
                $(this).html("<input type='number' class='hypothesized-grade'>");
                $(this).data("originalText", originalText);
                $(this).data("value", "");
            });

            table.find(".hypothesized-grade").on("change", function() {
                $(this).parent().data("value", $(this).val() + "%");
                grade_computation(table);
            });
            grade_computation(table);
        }
    })
}

function grade_computation(table) {
    const scoreColumn = table.find("tbody").find("tr td:last-child");
    console.log(scoreColumn);
    let total_avaliable = 0;
    let total_earned = 0;
    scoreColumn.each(function() {
        const val = $(this).data("value")
        console.log("value: ", val);
        const weight = parseFloat($(this).data("weight"));
        if (val.includes("Missing")) {
            total_avaliable += weight;
        } else if (val.includes("%")) {
            const percent = parseFloat(val.split("%")[0]);
            total_avaliable += weight;
            total_earned += percent * weight;
        }
    });

    const finalGrade = (total_earned / total_avaliable).toFixed(1) + "%";
    table.find("tfoot").find("tr td:last").text(finalGrade);
}