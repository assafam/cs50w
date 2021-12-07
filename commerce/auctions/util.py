from django.db.models import Max, Case, When, F, DecimalField

def annotate_with_current_price(auction_qs):
    """Get an Auction query set and annotate the current price (maximum bid or starting bid)"""
    return auction_qs.annotate(
        max_bid=Max('bids__bid')
    ).annotate(
        cur_price=Case(
            When(max_bid__isnull=False, then=F('max_bid')),
            default=F('starting_bid'),
            output_field=DecimalField()
        )
    )

def get_winning_bid(auction):
    """Return the winning bid of an auction"""
    return auction.bids.order_by("-bid", "creation_time").first()
