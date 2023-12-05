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