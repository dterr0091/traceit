import SwiftUI

extension Font {
    static func interRegular(size: CGFloat) -> Font {
        return Font.custom("Inter-Regular", size: size)
    }
    
    static func interMedium(size: CGFloat) -> Font {
        return Font.custom("Inter-Medium", size: size)
    }
    
    static func interBold(size: CGFloat) -> Font {
        return Font.custom("Inter-Bold", size: size)
    }
}

// Convenient extensions to replace system fonts with Inter
extension Font {
    static func interBody() -> Font {
        return interRegular(size: 17)
    }
    
    static func interTitle() -> Font {
        return interBold(size: 28)
    }
    
    static func interTitle2() -> Font {
        return interBold(size: 22)
    }
    
    static func interTitle3() -> Font {
        return interBold(size: 20)
    }
    
    static func interHeadline() -> Font {
        return interBold(size: 17)
    }
    
    static func interSubheadline() -> Font {
        return interRegular(size: 15)
    }
    
    static func interFootnote() -> Font {
        return interRegular(size: 13)
    }
    
    static func interCaption() -> Font {
        return interRegular(size: 12)
    }
} 